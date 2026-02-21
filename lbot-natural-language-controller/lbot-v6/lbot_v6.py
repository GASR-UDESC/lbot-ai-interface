#!/usr/bin/env python3
"""
LBot V6 - Seq2Seq Encoder-Decoder Translator
=============================================

Sequence-to-sequence model with Bahdanau (additive) attention for
translating Portuguese natural language commands to LBML V4 format.

Architecture:
- Encoder: Bidirectional GRU (2 layers, hidden=256)
- Attention: Bahdanau additive attention
- Decoder: GRU (2 layers, hidden=256) with attention context
- Separate vocabularies for encoder (PT chars) and decoder (LBML chars)

Key improvements over V5 (decoder-only GPT):
- Explicit encoder-decoder separation for comprehension vs generation
- Bidirectional encoder captures full input context
- Attention mechanism focuses on relevant input parts per output step
- Proper sequence-to-sequence training (not random window LM)
- Separate PT/LBML vocabularies (decoder only outputs valid LBML chars)
- Greedy decoding (deterministic, no temperature sampling)

Usage:
    python lbot_v6.py "ande 40 centímetros para frente"
    # Output: D40F;

    python lbot_v6.py --model lbot_translator_v6.pt "ande 40 centímetros para frente"

Or interactively:
    python lbot_v6.py

Requirements:
    - torch
    - lbot_translator_v6.pt (trained model file)
"""

import torch
import torch.nn as nn
import re
import sys
import os
import argparse
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ============================================================================
# SPECIAL TOKENS
# ============================================================================

PAD_TOKEN = '<PAD>'
SOS_TOKEN = '<SOS>'
EOS_TOKEN = '<EOS>'
UNK_TOKEN = '<UNK>'

SPECIAL_TOKENS = [PAD_TOKEN, SOS_TOKEN, EOS_TOKEN, UNK_TOKEN]
PAD_IDX = 0
SOS_IDX = 1
EOS_IDX = 2
UNK_IDX = 3


# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

@dataclass
class Seq2SeqConfig:
    """Configuration for the Seq2Seq encoder-decoder model."""
    # Vocabulary sizes (set during training from data)
    enc_vocab_size: int = 80      # Portuguese characters + special tokens
    dec_vocab_size: int = 20      # LBML characters + special tokens (D,R,F,B,L,;,0-9 + specials)

    # Embedding dimensions
    enc_emb_dim: int = 128
    dec_emb_dim: int = 64

    # Hidden dimensions
    hidden_dim: int = 256
    
    # GRU layers
    enc_layers: int = 2
    dec_layers: int = 2

    # Regularization
    dropout: float = 0.2

    # Sequence limits
    max_enc_len: int = 200       # Max input (Portuguese command) length
    max_dec_len: int = 100       # Max output (LBML) length


# ============================================================================
# VOCABULARY BUILDER
# ============================================================================

class Vocabulary:
    """Character-level vocabulary with special tokens."""

    def __init__(self, name: str = "vocab"):
        self.name = name
        self.stoi: Dict[str, int] = {}
        self.itos: Dict[int, str] = {}
        self.size = 0

        # Add special tokens
        for token in SPECIAL_TOKENS:
            self._add_token(token)

    def _add_token(self, token: str):
        if token not in self.stoi:
            idx = self.size
            self.stoi[token] = idx
            self.itos[idx] = token
            self.size += 1

    def build_from_texts(self, texts: List[str]):
        """Build vocabulary from a list of text strings."""
        chars = set()
        for text in texts:
            chars.update(text)
        for char in sorted(chars):
            self._add_token(char)

    def encode(self, text: str) -> List[int]:
        """Convert text to token indices."""
        return [self.stoi.get(c, UNK_IDX) for c in text]

    def decode(self, indices: List[int], strip_special: bool = True) -> str:
        """Convert token indices to text."""
        tokens = []
        for idx in indices:
            token = self.itos.get(idx, UNK_TOKEN)
            if strip_special and token in SPECIAL_TOKENS:
                if token == EOS_TOKEN:
                    break
                continue
            tokens.append(token)
        return ''.join(tokens)

    def __len__(self):
        return self.size


# ============================================================================
# ENCODER
# ============================================================================

class Encoder(nn.Module):
    """
    Bidirectional GRU encoder.
    
    Processes the full Portuguese input and produces:
    - outputs: hidden states at each position (for attention)
    - hidden: final hidden state (to initialize decoder)
    """

    def __init__(self, config: Seq2SeqConfig):
        super().__init__()
        self.hidden_dim = config.hidden_dim
        self.n_layers = config.enc_layers

        self.embedding = nn.Embedding(
            config.enc_vocab_size, config.enc_emb_dim, padding_idx=PAD_IDX
        )
        self.gru = nn.GRU(
            config.enc_emb_dim,
            config.hidden_dim,
            num_layers=config.enc_layers,
            dropout=config.dropout if config.enc_layers > 1 else 0,
            bidirectional=True,
            batch_first=True,
        )
        # Project bidirectional hidden to decoder hidden size
        self.fc_hidden = nn.Linear(config.hidden_dim * 2, config.hidden_dim)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, src: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            src: [batch, src_len] input token indices
        
        Returns:
            outputs: [batch, src_len, hidden*2] encoder hidden states
            hidden:  [n_layers, batch, hidden] final hidden for decoder init
        """
        # src: [batch, src_len]
        embedded = self.dropout(self.embedding(src))
        # embedded: [batch, src_len, emb_dim]

        outputs, hidden = self.gru(embedded)
        # outputs: [batch, src_len, hidden*2] (bidirectional concatenated)
        # hidden: [n_layers*2, batch, hidden]

        # Combine forward and backward hidden states for each layer
        # hidden shape: [n_layers*2, batch, hidden] -> [n_layers, batch, hidden]
        # Reshape: (layer0_fwd, layer0_bwd, layer1_fwd, layer1_bwd, ...)
        hidden = hidden.view(self.n_layers, 2, -1, self.hidden_dim)
        # hidden: [n_layers, 2, batch, hidden]
        hidden = torch.cat([hidden[:, 0, :, :], hidden[:, 1, :, :]], dim=2)
        # hidden: [n_layers, batch, hidden*2]
        hidden = torch.tanh(self.fc_hidden(hidden))
        # hidden: [n_layers, batch, hidden]

        return outputs, hidden


# ============================================================================
# ATTENTION
# ============================================================================

class BahdanauAttention(nn.Module):
    """
    Bahdanau (additive) attention mechanism.
    
    Computes attention weights over encoder outputs using the current
    decoder hidden state, then produces a context vector.
    """

    def __init__(self, config: Seq2SeqConfig):
        super().__init__()
        # Encoder outputs are bidirectional: hidden*2
        self.W_enc = nn.Linear(config.hidden_dim * 2, config.hidden_dim, bias=False)
        self.W_dec = nn.Linear(config.hidden_dim, config.hidden_dim, bias=False)
        self.V = nn.Linear(config.hidden_dim, 1, bias=False)

    def forward(
        self,
        decoder_hidden: torch.Tensor,
        encoder_outputs: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            decoder_hidden: [batch, hidden] current decoder hidden state
            encoder_outputs: [batch, src_len, hidden*2] all encoder outputs
            mask: [batch, src_len] True where input is padding
        
        Returns:
            context: [batch, hidden*2] weighted combination of encoder outputs
            attn_weights: [batch, src_len] attention distribution
        """
        # decoder_hidden: [batch, hidden] -> [batch, 1, hidden]
        dec_proj = self.W_dec(decoder_hidden.unsqueeze(1))
        # enc_proj: [batch, src_len, hidden]
        enc_proj = self.W_enc(encoder_outputs)

        # Energy: [batch, src_len, hidden] -> [batch, src_len, 1] -> [batch, src_len]
        energy = torch.tanh(enc_proj + dec_proj)
        attention = self.V(energy).squeeze(2)

        # Mask padding positions
        if mask is not None:
            attention = attention.masked_fill(mask, float('-inf'))

        attn_weights = torch.softmax(attention, dim=1)
        # attn_weights: [batch, src_len]

        # Context vector: weighted sum of encoder outputs
        context = torch.bmm(attn_weights.unsqueeze(1), encoder_outputs).squeeze(1)
        # context: [batch, hidden*2]

        return context, attn_weights


# ============================================================================
# DECODER
# ============================================================================

class Decoder(nn.Module):
    """
    GRU decoder with Bahdanau attention.
    
    At each step:
    1. Embed the previous output token
    2. Compute attention over encoder outputs
    3. Concatenate embedding + context and feed to GRU
    4. Predict next token
    """

    def __init__(self, config: Seq2SeqConfig):
        super().__init__()
        self.hidden_dim = config.hidden_dim
        self.n_layers = config.dec_layers

        self.embedding = nn.Embedding(
            config.dec_vocab_size, config.dec_emb_dim, padding_idx=PAD_IDX
        )
        self.attention = BahdanauAttention(config)

        # GRU input: embedding + context (hidden*2)
        self.gru = nn.GRU(
            config.dec_emb_dim + config.hidden_dim * 2,
            config.hidden_dim,
            num_layers=config.dec_layers,
            dropout=config.dropout if config.dec_layers > 1 else 0,
            batch_first=True,
        )

        # Output projection: hidden + context + embedding -> vocab
        self.fc_out = nn.Linear(
            config.hidden_dim + config.hidden_dim * 2 + config.dec_emb_dim,
            config.dec_vocab_size,
        )
        self.dropout = nn.Dropout(config.dropout)

    def forward(
        self,
        input_token: torch.Tensor,
        hidden: torch.Tensor,
        encoder_outputs: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Single decoding step.
        
        Args:
            input_token: [batch] previous token index
            hidden: [n_layers, batch, hidden] decoder hidden state
            encoder_outputs: [batch, src_len, hidden*2] encoder outputs
            mask: [batch, src_len] padding mask
        
        Returns:
            prediction: [batch, dec_vocab_size] logits for next token
            hidden: [n_layers, batch, hidden] updated hidden state
            attn_weights: [batch, src_len] attention weights
        """
        # input_token: [batch] -> [batch, 1]
        input_token = input_token.unsqueeze(1)

        # Embed: [batch, 1, emb_dim]
        embedded = self.dropout(self.embedding(input_token))

        # Attention: use top layer hidden state
        context, attn_weights = self.attention(
            hidden[-1], encoder_outputs, mask
        )
        # context: [batch, hidden*2]

        # Concatenate embedding and context for GRU input
        # [batch, 1, emb_dim + hidden*2]
        gru_input = torch.cat([embedded, context.unsqueeze(1)], dim=2)

        # GRU step
        output, hidden = self.gru(gru_input, hidden)
        # output: [batch, 1, hidden]
        output = output.squeeze(1)
        # output: [batch, hidden]

        # Predict next token
        prediction = self.fc_out(
            torch.cat([output, context, embedded.squeeze(1)], dim=1)
        )
        # prediction: [batch, dec_vocab_size]

        return prediction, hidden, attn_weights


# ============================================================================
# SEQ2SEQ MODEL
# ============================================================================

class Seq2Seq(nn.Module):
    """
    Full Seq2Seq model: Encoder + Attention + Decoder.
    """

    def __init__(self, config: Seq2SeqConfig):
        super().__init__()
        self.config = config
        self.encoder = Encoder(config)
        self.decoder = Decoder(config)

    def create_mask(self, src: torch.Tensor) -> torch.Tensor:
        """Create padding mask: True where src == PAD_IDX."""
        return src == PAD_IDX

    def forward(
        self,
        src: torch.Tensor,
        trg: torch.Tensor,
        teacher_forcing_ratio: float = 0.5,
    ) -> torch.Tensor:
        """
        Forward pass for training.
        
        Args:
            src: [batch, src_len] input token indices
            trg: [batch, trg_len] target token indices (with SOS prefix)
            teacher_forcing_ratio: probability of using ground truth as next input
        
        Returns:
            outputs: [batch, trg_len-1, dec_vocab_size] predictions (excluding SOS)
        """
        batch_size = src.size(0)
        trg_len = trg.size(1)
        dec_vocab_size = self.config.dec_vocab_size

        # Tensor to store decoder outputs
        outputs = torch.zeros(batch_size, trg_len - 1, dec_vocab_size, device=src.device)

        # Encode
        encoder_outputs, hidden = self.encoder(src)
        mask = self.create_mask(src)

        # First decoder input: <SOS> token
        input_token = trg[:, 0]  # [batch]

        for t in range(1, trg_len):
            prediction, hidden, _ = self.decoder(
                input_token, hidden, encoder_outputs, mask
            )
            outputs[:, t - 1, :] = prediction

            # Teacher forcing: use ground truth or predicted token
            if self.training and torch.rand(1).item() < teacher_forcing_ratio:
                input_token = trg[:, t]
            else:
                input_token = prediction.argmax(dim=1)

        return outputs

    @torch.no_grad()
    def translate(
        self,
        src: torch.Tensor,
        max_len: int = 100,
    ) -> Tuple[List[int], List[torch.Tensor]]:
        """
        Greedy decoding for inference.
        
        Args:
            src: [1, src_len] single input sequence
            max_len: maximum output length
        
        Returns:
            output_tokens: list of predicted token indices
            attention_weights: list of attention weight tensors
        """
        self.eval()

        # Encode
        encoder_outputs, hidden = self.encoder(src)
        mask = self.create_mask(src)

        # Start with <SOS>
        input_token = torch.tensor([SOS_IDX], device=src.device)

        output_tokens = []
        attention_weights = []

        for _ in range(max_len):
            prediction, hidden, attn_weights = self.decoder(
                input_token, hidden, encoder_outputs, mask
            )
            attention_weights.append(attn_weights.cpu())

            # Greedy: take argmax
            top_token = prediction.argmax(dim=1)
            token_id = top_token.item()

            if token_id == EOS_IDX:
                break

            output_tokens.append(token_id)
            input_token = top_token

        return output_tokens, attention_weights


# ============================================================================
# TRANSLATOR CLASS (High-level interface)
# ============================================================================

class LBotTranslatorV6:
    """LBot V6 Translator - Portuguese to LBML via Seq2Seq."""

    def __init__(self, model_path: str = 'lbot_translator_v6.pt'):
        """
        Load trained model from checkpoint.
        
        Args:
            model_path: Path to the .pt model file
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                f"Please ensure 'lbot_translator_v6.pt' is in the current directory."
            )

        print(f"🔄 Loading model from {model_path}...")

        # Load checkpoint
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)

        # Extract vocabularies
        self.enc_vocab = Vocabulary("encoder")
        self.enc_vocab.stoi = checkpoint['enc_stoi']
        self.enc_vocab.itos = checkpoint['enc_itos']
        self.enc_vocab.size = len(self.enc_vocab.stoi)

        self.dec_vocab = Vocabulary("decoder")
        self.dec_vocab.stoi = checkpoint['dec_stoi']
        self.dec_vocab.itos = checkpoint['dec_itos']
        self.dec_vocab.size = len(self.dec_vocab.stoi)

        # Recreate model
        config = checkpoint['config']
        self.model = Seq2Seq(config)
        self.model.load_state_dict(checkpoint['model'])
        self.model.eval()

        # Move to GPU if available
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if self.device == 'cuda':
            self.model = self.model.cuda()
            print(f"✅ Model loaded on GPU")
        else:
            print(f"✅ Model loaded on CPU")

        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"📊 Model info:")
        print(f"   • Encoder vocab: {self.enc_vocab.size} characters")
        print(f"   • Decoder vocab: {self.dec_vocab.size} characters")
        print(f"   • Parameters: {total_params:,}")
        print(f"   • Architecture: Seq2Seq (BiGRU + Bahdanau Attention)")

    def translate(self, command: str) -> str:
        """
        Translate Portuguese command to LBML V4 format.
        
        Args:
            command: Portuguese command (e.g., "ande 40 centímetros para frente")
        
        Returns:
            LBML command string (e.g., "D40F;") or "ERRO" if invalid.
        """
        # Encode input
        input_text = command.strip().lower()
        input_ids = self.enc_vocab.encode(input_text)

        # Convert to tensor: [1, src_len]
        src = torch.tensor([input_ids], dtype=torch.long, device=self.device)

        # Translate
        output_tokens, _ = self.model.translate(src, max_len=100)

        # Decode output
        result = self.dec_vocab.decode(output_tokens)

        # Validate LBML format
        if self._validate_lbml(result):
            return result

        # Try cleaning: keep only valid LBML characters
        cleaned = ''.join(c for c in result if c.isdigit() or c in 'DRFBL;')
        if cleaned and self._validate_lbml(cleaned):
            return cleaned

        return "ERRO"

    @staticmethod
    def _validate_lbml(code: str) -> bool:
        """Validate LBML V4 format: (D<num><FBLR>;|R<num><LR>;)+"""
        if not code:
            return False
        pattern = r'^(D\d+[FBLR];|R\d+[LR];)+$'
        return re.match(pattern, code) is not None


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def interactive_mode(translator: LBotTranslatorV6):
    """Run interactive translation mode."""
    print("\n🤖 === LBOT V6 TRANSLATOR (Seq2Seq) ===")
    print("Digite comandos em português ou 'sair' para terminar")
    print("Exemplos:")
    print("  • vá 40 centímetros para frente")
    print("  • gire 90 graus para direita")
    print("  • ande 25 centímetros para frente, depois vire 45 graus à esquerda")
    print("  • mova-se 30 centímetros para trás e depois gire 90 graus para direita")
    print()

    while True:
        try:
            command = input("🗣️  Comando: ").strip()

            if command.lower() in ['sair', 'exit', 'quit', '']:
                print("👋 Tchau!")
                break

            result = translator.translate(command)
            print(f"🤖 LBot: {result}\n")

        except KeyboardInterrupt:
            print("\n👋 Tchau!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LBot V6 Translator (Seq2Seq)')
    parser.add_argument('command', nargs='*', help='Portuguese command to translate')
    parser.add_argument(
        '--model', '-m', default='lbot_translator_v6.pt',
        help='Path to model file (default: lbot_translator_v6.pt)',
    )
    args = parser.parse_args()

    try:
        # Load translator
        translator = LBotTranslatorV6(args.model)

        # Check if command provided
        if args.command:
            # Single command mode
            command = ' '.join(args.command)
            result = translator.translate(command)
            print(result)
        else:
            # Interactive mode
            interactive_mode(translator)

    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("\nPara treinar o modelo:")
        print("  1. Gere o dataset: python generate_dataset_v6.py")
        print("  2. Execute o notebook: lbot_training_v6.ipynb no Google Colab")
        print("  3. Faça download do lbot_translator_v6.pt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
