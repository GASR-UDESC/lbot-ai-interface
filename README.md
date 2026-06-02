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


## 👥 Autores

- **Guilherme Mendes Rosa** - Desenvolvimento principal
- **GASR-UDESC** - Laboratório de Robótica