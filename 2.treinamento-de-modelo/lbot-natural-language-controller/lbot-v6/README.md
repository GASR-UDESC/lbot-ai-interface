# LBot V6 - Seq2Seq Encoder-Decoder Translator

Tradutor de linguagem natural (Português) para LBML V4 (LBot Movement Language) usando arquitetura **Seq2Seq com Bahdanau Attention**.

## Mudança de Arquitetura: V5 (GPT) → V6 (Seq2Seq)

O V5 usava um **decoder-only GPT** (modelo de linguagem causal) que atingiu apenas **61.1% de acurácia** no benchmark. O V6 resolve os problemas fundamentais com uma nova arquitetura:

### Diagnóstico dos Problemas do V5

| Problema | Impacto | Solução no V6 |
|----------|---------|---------------|
| Apenas 20 valores numéricos no treino (1,2,3...100 em steps) | ~55% das falhas em deslocamento | **TODOS os inteiros 1-100** no dataset |
| Bug: conectores sem espaço (`"depoisgire"`) | Falha em compostos | Conectores com espaço trailing (`", depois "`) |
| Decoder-only não separa compreensão de geração | Modelo confunde input/output | **Encoder-Decoder** com vocabulários separados |
| Random-window training (treina em trechos parciais) | Gradientes ruidosos | Batching por exemplo completo |
| LR constante 1e-3 sem schedule | Convergência subótima | Cosine annealing com warmup |
| Vocabulário limitado (4 verbos) | Frágil a variações | 10 verbos de deslocamento, 8 de rotação |
| Max 3 ações compostas | Limitação artificial | Até 4 ações compostas |

### Comparação de Arquiteturas

```
V5 (GPT - Decoder Only):
  "ande 40 centímetros para frente ->" → char-by-char generation → "D40F;"
  - Vocabulário unificado (~70 chars PT + LBML)
  - Sem separação encoder/decoder
  - Random-window training
  
V6 (Seq2Seq - Encoder-Decoder):
  Encoder(BiGRU): "ande 40 centímetros para frente" → hidden states
  Attention: foca no "40" ao gerar "40", no "frente" ao gerar "F"
  Decoder(GRU): hidden + attention → "D40F;" (vocab separado, só chars LBML)
```

## Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                    ENCODER                           │
│  Input: "ande 40 centímetros para frente"           │
│  Embedding(128) → BiGRU(256, 2 layers) → outputs   │
└──────────────────┬──────────────────────────────────┘
                   │ encoder outputs + hidden
                   ▼
┌─────────────────────────────────────────────────────┐
│              BAHDANAU ATTENTION                       │
│  decoder_hidden + encoder_outputs → context vector   │
│  Foca em partes relevantes do input a cada step      │
└──────────────────┬──────────────────────────────────┘
                   │ context
                   ▼
┌─────────────────────────────────────────────────────┐
│                    DECODER                           │
│  Embedding(64) + context → GRU(256, 2 layers)      │
│  → Linear → LBML vocab                              │
│  Output: "D40F;"                                     │
└─────────────────────────────────────────────────────┘
```

### Configuração

| Parâmetro         | Valor   |
|-------------------|---------|
| Encoder embedding | 128     |
| Decoder embedding | 64      |
| Hidden dim        | 256     |
| Encoder layers    | 2 (BiGRU) |
| Decoder layers    | 2 (GRU) |
| Dropout           | 0.2     |
| Params estimados  | ~2-3M   |

## Dataset V6

- **80.000 exemplos** (2× V5)
- **25k** deslocamento simples (31.25%)
- **25k** rotação simples (31.25%)
- **30k** compostos: 15k 2-ações + 10k 3-ações + 5k 4-ações (37.50%)

### Vocabulário Expandido

| Tipo | V5 (4) | V6 (10) |
|------|--------|---------|
| Deslocamento | vá, ande, mova-se, desloque-se | + se mova, caminhe, avance, percorra, se desloque, siga |
| Rotação | gire, vire, rotacione, faça uma rotação de | + rode, faça um giro de, faça uma curva de, mude a direção em |

### Valores Numéricos

- **V5:** 20 valores: 1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 75, 80, 90, 100
- **V6:** **TODOS os inteiros 1-100** (100 valores)

## Treinamento

| Parâmetro | V5 | V6 |
|-----------|-----|-----|
| Optimizer | AdamW, lr=1e-3 | AdamW, lr=3e-4 |
| LR Schedule | Nenhum | Cosine annealing + warmup (500 steps) |
| Gradient Clip | Nenhum | max_norm=1.0 |
| Data Split | 90/10 por caractere | 85/10/5 por exemplo |
| Batch Size | 32 | 64 |
| Teacher Forcing | N/A | 0.5 → 0.0 (linear decay) |
| Early Stopping | Não | Sim (patience=10) |
| Max Epochs | 5000 iters | 100 epochs |

## Como Usar

### 1. Gerar o Dataset

```bash
cd lbot-v6
python generate_dataset_v6.py
```

Gera `lbot_dataset_v6.txt` (~80k exemplos).

### 2. Treinar o Modelo (Google Colab)

1. Abra `lbot_training_v6.ipynb` no Google Colab
2. Selecione Runtime → GPU (T4)
3. Upload `lbot_dataset_v6.txt`
4. Execute todas as células
5. Download `lbot_translator_v6.pt`

Tempo estimado: ~20-40 min no T4.

### 3. Usar o Tradutor

```bash
# Comando único
python lbot_v6.py "ande 40 centímetros para frente"
# Output: D40F;

# Modo interativo
python lbot_v6.py

# Especificar modelo
python lbot_v6.py --model lbot_translator_v6.pt "gire 90 graus para direita"
```

### 4. Usar como Módulo Python

```python
from lbot_v6 import LBotTranslatorV6

translator = LBotTranslatorV6('lbot_translator_v6.pt')

# Simples
result = translator.translate("ande 40 centímetros para frente")
print(result)  # D40F;

# Composto
result = translator.translate("vá 30 centímetros para frente e depois gire 90 graus para direita")
print(result)  # D30F;R90R;
```

## Benchmark Meta

Testado contra o [benchmark_test_set.txt](../benchmark/benchmark_test_set.txt) (342 casos):

| Categoria | V5 | Meta V6 |
|-----------|-----|---------|
| **Overall** | 61.1% | 90%+ |
| Rotação simples | 100% | 100% |
| Deslocamento simples | 44.7% | 90%+ |
| Composto 2 ações | 28.3% | 80%+ |
| Composto 3 ações | 32.5% | 75%+ |

## Formato LBML V4

```
Deslocamento: D<valor><direção>;
  D40F;    → 40cm para frente
  D25B;    → 25cm para trás
  D10L;    → 10cm para esquerda
  D60R;    → 60cm para direita

Rotação: R<ângulo><direção>;
  R90R;    → 90° para direita (sentido horário)
  R45L;    → 45° para esquerda (sentido anti-horário)

Composto: concatenação
  D40F;R90R;D20L;  → 40cm frente, gira 90° direita, 20cm esquerda
```

## Estrutura de Arquivos

```
lbot-v6/
├── generate_dataset_v6.py    # Gerador do dataset (80k exemplos)
├── lbot_v6.py                # Modelo Seq2Seq + inferência + CLI
├── lbot_training_v6.ipynb    # Notebook de treino (Google Colab)
├── lbot_dataset_v6.txt       # Dataset gerado (após rodar generator)
├── lbot_translator_v6.pt     # Modelo treinado (após treino)
└── README.md                 # Esta documentação
```
