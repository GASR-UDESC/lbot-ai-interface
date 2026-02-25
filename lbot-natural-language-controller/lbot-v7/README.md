# LBot V7 — Seq2Seq Robusto com Preprocessing

## Visão Geral

A V7 é a evolução da V6, mantendo a **mesma arquitetura** (BiGRU Seq2Seq + Bahdanau Attention) mas adicionando:

1. **Pipeline de preprocessing** para normalizar inputs não-padrão
2. **Dataset aumentado (~220k exemplos)** com variações realistas
3. **Suporte a múltiplas unidades** (metros, mm, km, jardas, passos → centímetros)

### Problema que resolve

A V6 era muito rígida — falhava com:
- Abreviações: `40cm`, `90°`
- Sem acentos: `centimetros`, `anti-horario`
- Sem pontuação: `ande 40 centímetros para frente depois gire 90 graus`
- Linguagem informal: `vai`, `roda`, `pra frente`
- Números por extenso: `quarenta`, `noventa`
- Outras unidades: `2 metros`, `3 passos`

A V7 resolve tudo isso.

## Arquitetura

```
Input → Preprocessing Pipeline → Seq2Seq Model → LBML Output
             │                        │
             ├─ Unit conversion       ├─ Encoder: BiGRU (2L, 256, bidirectional)
             ├─ Abbreviation expand   ├─ Attention: Bahdanau (additive)
             ├─ Number words→digits   └─ Decoder: GRU (2L, 256)
             ├─ Accent normalization
             ├─ Punctuation fix
             └─ Informal normalization
```

### Comparação V6 vs V7

| Parâmetro | V6 | V7 |
|-----------|-----|-----|
| Dataset | 80k exemplos | ~220k exemplos |
| Unidades | Só centímetros | cm, m, mm, km, yd, passos |
| Preprocessing | `.strip().lower()` | Pipeline completo (7 etapas) |
| Informal | Não | Sim (vai, roda, pra frente, etc.) |
| Max input len | 200 | 250 |
| Batch size | 64 | 128 |
| Max epochs | 100 | 150 |
| Early stopping | 10 epochs | 15 epochs |

## Pipeline de Preprocessing

O preprocessing acontece **antes** de enviar ao modelo, em 7 etapas:

```
1. Cleanup básico         "  vai  40cm  pra  frente  "  → "vai 40cm pra frente"
2. Informal → formal      "vai 40cm pra frente"         → "vá 40cm para frente"
3. Números extenso→dígito "quarenta"                     → "40"
4. Conversão de unidades  "2 metros"                     → "200 centímetros"
5. Expand abreviações     "40cm"                         → "40 centímetros"
6. Fix acentos            "centimetros"                  → "centímetros"
7. Normalizar pontuação   "... frente depois gire ..."   → "... frente, depois gire ..."
```

### Tabela de Conversão de Unidades

| Unidade | Fator | Exemplo |
|---------|-------|---------|
| centímetro (cm) | ×1 | 40 cm → 40 centímetros |
| metro (m) | ×100 | 2 m → 200 centímetros |
| milímetro (mm) | ×0.1 | 500 mm → 50 centímetros |
| quilômetro (km) | ×100000 | 1 km → 100000 centímetros |
| jarda (yd) | ×91.44 | 1 yd → 91 centímetros |
| passo | ×75 | 3 passos → 225 centímetros |

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `lbot_v7.py` | Modelo + preprocessing + CLI |
| `generate_dataset_v7.py` | Gerador de dataset aumentado |
| `lbot_training_v7.ipynb` | Notebook de treinamento (Google Colab) |
| `test_robustness.py` | Suite de testes de robustez |
| `lbot_dataset_v7.txt` | Dataset gerado (~220k linhas) |
| `lbot_translator_v7.pt` | Modelo treinado |

## Uso

### Tradução via CLI

```bash
# Comando simples
python lbot_v7.py "ande 40 centímetros para frente"

# Com abreviação
python lbot_v7.py "ande 40cm pra frente"

# Multi-unidade
python lbot_v7.py "ande 2 metros para frente"

# Número por extenso
python lbot_v7.py "ande quarenta centímetros para frente"

# Informal + abreviação + multi-unidade
python lbot_v7.py "vai 2m pra frente depois roda 90° pra esquerda"

# Ver preprocessing detalhado
python lbot_v7.py --verbose "vai 40cm pra frente"

# Só testar preprocessing (sem modelo)
python lbot_v7.py --preprocess-only "vai 2m pra frente"

# Modo interativo
python lbot_v7.py
```

### Gerar Dataset

```bash
python generate_dataset_v7.py
# Gera lbot_dataset_v7.txt com ~220k exemplos
```

### Treinar Modelo

1. Gere o dataset: `python generate_dataset_v7.py`
2. Abra `lbot_training_v7.ipynb` no Google Colab
3. Faça upload do `lbot_dataset_v7.txt`
4. Execute todas as células
5. Baixe `lbot_translator_v7.pt`

### Rodar Testes

```bash
# Só preprocessing (não precisa do modelo)
python test_robustness.py

# Com modelo treinado
python test_robustness.py --model lbot_translator_v7.pt
```

## Data Augmentation

O `generate_dataset_v7.py` gera variações automáticas de cada exemplo:

| Tipo | Exemplo Original | Variação |
|------|-----------------|----------|
| Sem acentos | centímetros | centimetros |
| Abreviação | centímetros | cm |
| Sem pontuação | ..., depois ... | ... depois ... |
| Typos | centímetros | centímetrso |
| Numeros extenso | 40 | quarenta |
| Informal | vá para frente | vai pra frente |

**Distribuição do dataset:**
- ~80k exemplos limpos (padrão, como V6)
- ~140k exemplos aumentados (com variações)
- Total: ~220k exemplos

## Formato LBML V4 (inalterado)

```
D<valor_cm><direção>;   →  Deslocamento (F=Frente, B=Trás, L=Esquerda, R=Direita)
R<ângulo><direção>;     →  Rotação (L=Anti-horário, R=Horário)
```

Exemplos:
- `D40F;` → Ande 40cm para frente
- `R90R;` → Gire 90° para direita
- `D200F;R90R;D50L;` → Ande 2m para frente, gire 90° direita, ande 50cm esquerda

## Dependências

```
torch>=1.9.0
numpy
matplotlib (só para treinamento)
tqdm (só para treinamento)
```
