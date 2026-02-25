#!/usr/bin/env python3
"""
LBot V7 - Robust Seq2Seq Translator with Input Preprocessing
=============================================================

Evolution of V6's Seq2Seq encoder-decoder architecture, adding a robust
input preprocessing pipeline that handles:
- Unit conversion (metros, mm, km, jardas, passos → centímetros)
- Abbreviation expansion (cm → centímetros, ° → graus)
- Numbers written as words (quarenta → 40)
- Missing accents (centimetros → centímetros)
- Missing punctuation (connector normalization)
- Informal/colloquial language

Architecture (same as V6):
- Encoder: Bidirectional GRU (2 layers, hidden=256)
- Attention: Bahdanau additive attention
- Decoder: GRU (2 layers, hidden=256) with attention context
- Separate vocabularies for encoder (PT chars) and decoder (LBML chars)

Key improvements over V6:
- Robust input preprocessing pipeline (unit conversion, abbreviations, etc.)
- ~220k training examples (2.75× V6's 80k) with data augmentation
- Handles informal/non-standard inputs gracefully

Usage:
    python lbot_v7.py "ande 40cm pra frente"
    python lbot_v7.py "ande 2 metros para frente"
    python lbot_v7.py "vai quarenta centímetros pra frente"
    python lbot_v7.py "ande 40 centimetros para frente"
    python lbot_v7.py --model lbot_translator_v7.pt "ande 3 passos pra frente"

Or interactively:
    python lbot_v7.py

Requirements:
    - torch
    - lbot_translator_v7.pt (trained model file)
"""

import torch
import torch.nn as nn
import re
import sys
import os
import argparse
import unicodedata
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
# INPUT PREPROCESSING PIPELINE
# ============================================================================

# --- Number words (Portuguese) ---

_UNITS = {
    'zero': 0, 'um': 1, 'uma': 1, 'dois': 2, 'duas': 2, 'três': 3, 'tres': 3,
    'quatro': 4, 'cinco': 5, 'seis': 6, 'sete': 7, 'oito': 8, 'nove': 9,
    'dez': 10, 'onze': 11, 'doze': 12, 'treze': 13, 'quatorze': 14, 'catorze': 14,
    'quinze': 15, 'dezesseis': 16, 'dezessete': 17, 'dezoito': 18, 'dezenove': 19,
}

_TENS = {
    'vinte': 20, 'trinta': 30, 'quarenta': 40, 'cinquenta': 50,
    'cinqüenta': 50, 'sessenta': 60, 'setenta': 70, 'oitenta': 80, 'noventa': 90,
}

_HUNDREDS = {
    'cem': 100, 'cento': 100, 'duzentos': 200, 'duzentas': 200,
    'trezentos': 300, 'trezentas': 300, 'quatrocentos': 400, 'quatrocentas': 400,
    'quinhentos': 500, 'quinhentas': 500, 'seiscentos': 600, 'seiscentas': 600,
    'setecentos': 700, 'setecentas': 700, 'oitocentos': 800, 'oitocentas': 800,
    'novecentos': 900, 'novecentas': 900,
}

_ALL_NUMBER_WORDS = set(_UNITS) | set(_TENS) | set(_HUNDREDS) | {'e'}

def _words_to_number(words: List[str]) -> Optional[int]:
    """Convert a sequence of Portuguese number words to an integer.
    
    Supports values from 0 to 999.
    Examples:
        ['quarenta'] -> 40
        ['vinte', 'e', 'cinco'] -> 25
        ['cento', 'e', 'quarenta', 'e', 'dois'] -> 142
        ['cem'] -> 100
    """
    # Filter out 'e' connectors
    filtered = [w for w in words if w != 'e']
    if not filtered:
        return None
    
    total = 0
    for w in filtered:
        if w in _HUNDREDS:
            total += _HUNDREDS[w]
        elif w in _TENS:
            total += _TENS[w]
        elif w in _UNITS:
            total += _UNITS[w]
        else:
            return None
    
    return total if total > 0 or (len(filtered) == 1 and filtered[0] == 'zero') else None


def _replace_number_words(text: str) -> str:
    """Replace Portuguese number words with digits.
    
    Examples:
        "quarenta centímetros" -> "40 centímetros"
        "vinte e cinco centímetros" -> "25 centímetros"
        "cento e oitenta graus" -> "180 graus"
    """
    words = text.split()
    result = []
    i = 0
    
    while i < len(words):
        word_lower = words[i].lower()
        
        # Check if this word starts a number sequence
        if word_lower in _ALL_NUMBER_WORDS and word_lower != 'e':
            # Collect consecutive number words
            num_words = []
            j = i
            while j < len(words) and words[j].lower() in _ALL_NUMBER_WORDS:
                num_words.append(words[j].lower())
                j += 1
            
            # Try to convert
            number = _words_to_number(num_words)
            if number is not None:
                result.append(str(number))
                i = j
                continue
        
        result.append(words[i])
        i += 1
    
    return ' '.join(result)


# --- Unit conversion ---

# Unit patterns and their conversion factors to centimeters
_UNIT_CONVERSIONS = {
    # metros
    r'(\d+(?:[.,]\d+)?)\s*(?:metros?|m\b)': ('m', 100),
    # quilômetros (with and without accent)
    r'(\d+(?:[.,]\d+)?)\s*(?:quil[oô]metros?|km\b)': ('km', 100000),
    # milímetros (with and without accent)
    r'(\d+(?:[.,]\d+)?)\s*(?:mil[ií]metros?|mm\b)': ('mm', 0.1),
    # jardas
    r'(\d+(?:[.,]\d+)?)\s*(?:jardas?|yd\b)': ('yd', 91.44),
    # passos
    r'(\d+(?:[.,]\d+)?)\s*(?:passos?\b)': ('passo', 75),
}

def _convert_units(text: str) -> str:
    """Convert various distance units to centimeters.
    
    Examples:
        "2 metros" -> "200 centímetros"
        "500mm" -> "50 centímetros"
        "3 passos" -> "225 centímetros"
        "1 jarda" -> "91 centímetros"
    """
    # Process each unit type — order matters: longer patterns first
    # to avoid "quilômetros" matching "metros"
    ordered_patterns = [
        # quilômetros first (contains "metros")
        (r'(\d+(?:[.,]\d+)?)\s*(?:quil[oô]metros?|quilometros?|km)\b', 100000),
        # milímetros before metros
        (r'(\d+(?:[.,]\d+)?)\s*(?:mil[ií]metros?|milimetros?|mm)\b', 0.1),
        # jardas
        (r'(\d+(?:[.,]\d+)?)\s*(?:jardas?|yd)\b', 91.44),
        # passos
        (r'(\d+(?:[.,]\d+)?)\s*(?:passos?)\b', 75),
        # metros — MUST be after quilômetros and milímetros
        (r'(\d+(?:[.,]\d+)?)\s*(?:metros?|m)\b(?!\w)', 100),
    ]
    
    for pattern, factor in ordered_patterns:
        def _replace(match, f=factor):
            value_str = match.group(1).replace(',', '.')
            value = float(value_str)
            cm_value = round(value * f)
            unit = "centímetro" if cm_value == 1 else "centímetros"
            return f"{cm_value} {unit}"
        
        text = re.sub(pattern, _replace, text, flags=re.IGNORECASE)
    
    return text


# --- Abbreviation expansion ---

def _expand_abbreviations(text: str) -> str:
    """Expand common abbreviations.
    
    Examples:
        "40cm" -> "40 centímetros"
        "40 cm" -> "40 centímetros"
        "90°" -> "90 graus"
    """
    # cm -> centímetros (with optional space)
    text = re.sub(r'(\d+)\s*cm\b', r'\1 centímetros', text, flags=re.IGNORECASE)
    
    # ° -> graus
    text = re.sub(r'(\d+)\s*°', r'\1 graus', text)
    
    return text


# --- Accent normalization ---

_ACCENT_FIXES = {
    'centimetros': 'centímetros',
    'centimetro': 'centímetro',
    'direcao': 'direção',
    'horario': 'horário',
    'anti-horario': 'anti-horário',
    'antihorario': 'anti-horário',
    'atras': 'atrás',
    'a frente': 'à frente',
    'a esquerda': 'à esquerda',
    'a direita': 'à direita',
    'rotacao': 'rotação',
    'angulo': 'ângulo',
    'desloque-se': 'desloque-se',  # already correct
    'mova-se': 'mova-se',          # already correct
}

def _fix_accents(text: str) -> str:
    """Fix common missing accents in Portuguese text.
    
    Examples:
        "centimetros" -> "centímetros"
        "a frente" -> "à frente"
        "atras" -> "atrás"
    """
    for wrong, correct in _ACCENT_FIXES.items():
        # Use word boundary matching for multi-word patterns
        if ' ' in wrong:
            text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text)
        else:
            text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text)
    return text


# --- Punctuation normalization ---

_CONNECTOR_WORDS = [
    'depois', 'em seguida', 'então', 'entao', 'por fim',
    'aí depois', 'ai depois', 'e aí', 'e ai', 'daí', 'dai',
]

def _normalize_punctuation(text: str) -> str:
    """Insert commas before connectors when missing.
    
    Examples:
        "ande 40 centímetros para frente depois gire 90 graus" 
        -> "ande 40 centímetros para frente, depois gire 90 graus"
    """
    for connector in sorted(_CONNECTOR_WORDS, key=len, reverse=True):
        # Match connector preceded by a word character and whitespace (no comma/semicolon before)
        pattern = r'(\w)\s+(' + re.escape(connector) + r')\b'
        text = re.sub(pattern, r'\1, \2', text, flags=re.IGNORECASE)
    
    return text


# --- Informal language normalization ---

_INFORMAL_REPLACEMENTS = [
    # Informal verbs -> standard forms
    (r'\bvai\b', 'vá'),
    (r'\bsegue\b', 'siga'),
    (r'\bmexe\b', 'mova-se'),
    (r'\bbota pra andar\b', 'ande'),
    (r'\bse mexe\b', 'se mova'),
    (r'\broda\b', 'rode'),
    (r'\bdobra\b', 'gire'),
    (r'\bfaz uma curva\b', 'faça uma curva'),
    (r'\bmuda de dire[çc][ãa]o\b', 'mude a direção'),
    
    # Informal directions
    (r'\breto\b', 'para frente'),
    (r'\bde r[ée]\b', 'para trás'),
    (r'\bde costas\b', 'para trás'),
    
    # Fillers and informal connectors
    (r'\buns\s+(\d)', r'\1'),  # "uns 40" -> "40"
    (r'\baí\s+depois\b', 'depois'),
    (r'\bai\s+depois\b', 'depois'),
    (r'\be\s+aí\b', 'e depois'),
    (r'\be\s+ai\b', 'e depois'),
    (r'\bdaí\b', 'depois'),
    (r'\bdai\b', 'depois'),
]

def _normalize_informal(text: str) -> str:
    """Normalize informal/colloquial language to standard forms.
    
    Examples:
        "vai 40cm pra frente" -> "vá 40cm pra frente"
        "roda 90° pra esquerda" -> "rode 90° pra esquerda"
        "uns 40 centímetros" -> "40 centímetros"
    """
    for pattern, replacement in _INFORMAL_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def preprocess_input(text: str) -> str:
    """
    Full input preprocessing pipeline.
    
    Transforms non-standard input into a normalized form that the 
    model can handle reliably. Steps (in order):
    
    1. Basic cleanup (strip, collapse whitespace)
    2. Informal language normalization
    3. Number words → digits
    4. Unit conversion (metros, mm, km, jardas, passos → centímetros)
    5. Abbreviation expansion (cm, °)
    6. Accent fixes
    7. Punctuation normalization (insert commas before connectors)
    
    Args:
        text: Raw user input
    
    Returns:
        Normalized text ready for the model
    
    Examples:
        "ande 40cm pra frente" -> "ande 40 centímetros pra frente"
        "vai 2 metros pra frente" -> "vá 2 metros pra frente" -> "vá 200 centímetros pra frente"
        "ande quarenta centimetros para frente" -> "ande 40 centímetros para frente"
        "ande 40 centímetros para frente depois gire 90 graus" 
            -> "ande 40 centímetros para frente, depois gire 90 graus"
    """
    # 1. Basic cleanup
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    # 2. Informal language normalization
    text = _normalize_informal(text)
    
    # 3. Number words → digits (before unit conversion)
    text = _replace_number_words(text)
    
    # 4. Unit conversion (metros, mm, etc. → centímetros)
    text = _convert_units(text)
    
    # 5. Abbreviation expansion (cm → centímetros, ° → graus)
    text = _expand_abbreviations(text)
    
    # 6. Accent fixes
    text = _fix_accents(text)
    
    # 7. Punctuation normalization
    text = _normalize_punctuation(text)
    
    return text


# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

@dataclass
class Seq2SeqConfig:
    """Configuration for the Seq2Seq encoder-decoder model."""
    # Vocabulary sizes (set during training from data)
    enc_vocab_size: int = 100     # Portuguese characters + special tokens (larger for augmented data)
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
    max_enc_len: int = 250       # Increased from 200 (number words make inputs longer)
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
        embedded = self.dropout(self.embedding(src))
        outputs, hidden = self.gru(embedded)

        # Combine forward and backward hidden states for each layer
        hidden = hidden.view(self.n_layers, 2, -1, self.hidden_dim)
        hidden = torch.cat([hidden[:, 0, :, :], hidden[:, 1, :, :]], dim=2)
        hidden = torch.tanh(self.fc_hidden(hidden))

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
        dec_proj = self.W_dec(decoder_hidden.unsqueeze(1))
        enc_proj = self.W_enc(encoder_outputs)

        energy = torch.tanh(enc_proj + dec_proj)
        attention = self.V(energy).squeeze(2)

        if mask is not None:
            attention = attention.masked_fill(mask, float('-inf'))

        attn_weights = torch.softmax(attention, dim=1)
        context = torch.bmm(attn_weights.unsqueeze(1), encoder_outputs).squeeze(1)

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
        input_token = input_token.unsqueeze(1)
        embedded = self.dropout(self.embedding(input_token))

        context, attn_weights = self.attention(
            hidden[-1], encoder_outputs, mask
        )

        gru_input = torch.cat([embedded, context.unsqueeze(1)], dim=2)
        output, hidden = self.gru(gru_input, hidden)
        output = output.squeeze(1)

        prediction = self.fc_out(
            torch.cat([output, context, embedded.squeeze(1)], dim=1)
        )

        return prediction, hidden, attn_weights


# ============================================================================
# SEQ2SEQ MODEL
# ============================================================================

class Seq2Seq(nn.Module):
    """Full Seq2Seq model: Encoder + Attention + Decoder."""

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

        outputs = torch.zeros(batch_size, trg_len - 1, dec_vocab_size, device=src.device)
        encoder_outputs, hidden = self.encoder(src)
        mask = self.create_mask(src)

        input_token = trg[:, 0]

        for t in range(1, trg_len):
            prediction, hidden, _ = self.decoder(
                input_token, hidden, encoder_outputs, mask
            )
            outputs[:, t - 1, :] = prediction

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

        encoder_outputs, hidden = self.encoder(src)
        mask = self.create_mask(src)

        input_token = torch.tensor([SOS_IDX], device=src.device)

        output_tokens = []
        attention_weights = []

        for _ in range(max_len):
            prediction, hidden, attn_weights = self.decoder(
                input_token, hidden, encoder_outputs, mask
            )
            attention_weights.append(attn_weights.cpu())

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

class LBotTranslatorV7:
    """LBot V7 Translator - Portuguese to LBML via Seq2Seq with preprocessing."""

    def __init__(self, model_path: str = 'lbot_translator_v7.pt'):
        """
        Load trained model from checkpoint.
        
        Args:
            model_path: Path to the .pt model file
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                f"Please ensure 'lbot_translator_v7.pt' is in the current directory."
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
        print(f"   • Preprocessing: Enabled (unit conversion, abbreviations, accents, etc.)")

    def translate(self, command: str) -> str:
        """
        Translate Portuguese command to LBML V4 format.
        
        Applies the full preprocessing pipeline before translating,
        handling abbreviations, missing accents, unit conversion, etc.
        
        Args:
            command: Portuguese command (e.g., "ande 40cm pra frente")
        
        Returns:
            LBML command string (e.g., "D40F;") or "ERRO" if invalid.
        """
        # Preprocess input (unit conversion, abbreviations, accents, etc.)
        preprocessed = preprocess_input(command)
        
        # Encode input
        input_text = preprocessed.strip().lower()
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

    def translate_verbose(self, command: str) -> Tuple[str, str, str]:
        """
        Translate with verbose output showing preprocessing steps.
        
        Returns:
            (original, preprocessed, lbml_result)
        """
        preprocessed = preprocess_input(command)
        result = self.translate(command)
        return command, preprocessed, result

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

def interactive_mode(translator: LBotTranslatorV7):
    """Run interactive translation mode."""
    print("\n🤖 === LBOT V7 TRANSLATOR (Seq2Seq + Preprocessing) ===")
    print("Digite comandos em português ou 'sair' para terminar")
    print("Agora com suporte a:")
    print("  • Abreviações: 'ande 40cm pra frente'")
    print("  • Unidades: 'ande 2 metros para frente'")
    print("  • Sem acentos: 'ande 40 centimetros para frente'")
    print("  • Números por extenso: 'ande quarenta centímetros para frente'")
    print("  • Linguagem informal: 'vai 40cm pra frente'")
    print("  • Sem vírgulas: 'ande 40cm pra frente depois gire 90 graus'")
    print()
    print("Exemplos:")
    print("  • vá 40 centímetros para frente")
    print("  • ande 2 metros para trás")
    print("  • gire 90° pra direita")
    print("  • vai 3 passos pra frente, depois roda 90 graus pra esquerda")
    print()

    while True:
        try:
            command = input("🗣️  Comando: ").strip()

            if command.lower() in ['sair', 'exit', 'quit', '']:
                print("👋 Tchau!")
                break

            original, preprocessed, result = translator.translate_verbose(command)
            
            # Show preprocessing if it changed the input
            if original.strip().lower() != preprocessed.strip().lower():
                print(f"🔧 Preprocessed: {preprocessed}")
            
            print(f"🤖 LBot: {result}\n")

        except KeyboardInterrupt:
            print("\n👋 Tchau!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LBot V7 Translator (Seq2Seq + Preprocessing)')
    parser.add_argument('command', nargs='*', help='Portuguese command to translate')
    parser.add_argument(
        '--model', '-m', default='lbot_translator_v7.pt',
        help='Path to model file (default: lbot_translator_v7.pt)',
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Show preprocessing steps',
    )
    parser.add_argument(
        '--preprocess-only', '-p', action='store_true',
        help='Only show preprocessing result (no model needed)',
    )
    args = parser.parse_args()

    # Preprocess-only mode (no model needed)
    if args.preprocess_only:
        if args.command:
            command = ' '.join(args.command)
            print(f"Input:        {command}")
            print(f"Preprocessed: {preprocess_input(command)}")
        else:
            print("🔧 Preprocessing-only mode. Type 'sair' to exit.")
            while True:
                try:
                    command = input("Input: ").strip()
                    if command.lower() in ['sair', 'exit', 'quit', '']:
                        break
                    print(f"Preprocessed: {preprocess_input(command)}\n")
                except (KeyboardInterrupt, EOFError):
                    break
        return

    try:
        # Load translator
        translator = LBotTranslatorV7(args.model)

        # Check if command provided
        if args.command:
            command = ' '.join(args.command)
            if args.verbose:
                original, preprocessed, result = translator.translate_verbose(command)
                print(f"Input:        {original}")
                print(f"Preprocessed: {preprocessed}")
                print(f"LBML:         {result}")
            else:
                result = translator.translate(command)
                print(result)
        else:
            # Interactive mode
            interactive_mode(translator)

    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("\nPara treinar o modelo:")
        print("  1. Gere o dataset: python generate_dataset_v7.py")
        print("  2. Execute o notebook: lbot_training_v7.ipynb no Google Colab")
        print("  3. Faça download do lbot_translator_v7.pt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
