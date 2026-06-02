# L-Bot AI Interface

O **L-Bot AI Interface** é uma plataforma integrada para controle e simulação de robôs E-Puck com capacidades de inteligência artificial. O projeto combina simulação 3D, controle via linguagem natural, geração de dados para treinamento e interfaces web modernas.

## 📋 Estrutura do Projeto

```
1.coleta-de-dados/lbot-datagen          → Geração de datasets para treinamento
2.treinamento-de-modelo/lbot-natural-language-controller → Tradutor NL→LBML (v3-v7, modelo RASA)
3.controlador/lbot-mcp                  → MCP Server + Harness (FastMCP, OpenAI SDK)
3.controlador/lbot-simulator-web        → Simulador 3D Web (Three.js, cannon-es, Express)
```

## 🚀 Funcionalidades

### 🎮 Simulador 3D Web (`3.controlador/lbot-simulator-web`)
- Simulação visual em tempo real de robôs E-Puck
- Interface web responsiva
- Controle direto via browser
- Visualização 3D com Three.js
- Câmera 1ª pessoa e sensores de proximidade via API REST

### 🤖 Controle via Linguagem Natural (`2.treinamento-de-modelo/lbot-natural-language-controller`)
- Modelo GPT customizado para comandos de robô
- Tradução de linguagem natural para comandos de movimento
- API REST para integração
- Cliente web Angular

### 📊 Geração de Dados (`1.coleta-de-dados/lbot-datagen`)
- Backend Spring Boot para processamento
- Frontend Angular para visualização
- Geração automática de datasets de treinamento
- API REST completa

### 🔌 MCP Server + Harness (`3.controlador/lbot-mcp`)
- MCP Server com 3 tools (câmera, proximidade, deslocamento)
- CLI interativo com loop agêntico ReAct
- Integração com LM Studio via OpenAI SDK
- Backend plugável (simulador ou hardware real)

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologias |
|------------|-------------|
| **Frontend** | Angular 18+, TypeScript, HTML5/CSS3 |
| **Backend** | Spring Boot 3.5, Java, Maven |
| **IA/ML** | PyTorch, Python, GPT personalizado |
| **Simulação** | Three.js, WebGL, Enki Robotics |
| **Comunicação** | Socket TCP, REST API, FastAPI |
| **Build** | CMake, npm, Maven |


## 🏃 Como Rodar (Simulador + Harness)

Pré-requisitos: **Node.js 18+**, **npm**, **Python 3.12**, **uv** e **LM Studio** rodando localmente com um modelo carregado.

### 1. Simulador 3D (com frontend)

```bash
cd 3.controlador/lbot-simulator-web
npm install       # apenas na primeira vez
npm run dev
```

Abra `http://localhost:5173` no navegador para ver o robô na arena.

### 2. Harness (CLI com IA)

O harness roda num **venv local** dentro de `3.controlador/lbot-mcp/` — não instala nada na sua máquina:

```bash
cd 3.controlador/lbot-mcp

# Criar venv e instalar (apenas na primeira vez)
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"

# Executar o harness
.venv/bin/lbot-harness
```

Comandos no prompt `🤖 >`:
- `tire uma foto`
- `qual a distância até a parede?`
- `ande 30cm para frente`
- `explore a sala e me diga o que você vê`
- `/help`, `/tools`, `/exit`
- `Ctrl+C` durante execução → interrompe o agente sem fechar o CLI

### LM Studio

Certifique-se de que o **LM Studio** está rodando com um modelo compatível com *function calling* (ex: Qwen 2.5, Mistral, Llama 3) e a porta padrão `1234`.


## 👥 Autores

- **Guilherme Mendes Rosa** - Desenvolvimento principal
- **GASR-UDESC** - Laboratório de Robótica