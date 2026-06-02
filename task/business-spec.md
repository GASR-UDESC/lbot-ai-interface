# Especificacao de Negocio: Adicionar Objetos e Itens no Simulador

## Contexto

O projeto LBot possui um simulador 3D web (`3.controlador/lbot-simulator-web`) que já inclui:
- Robô E-Puck com movimentação via LBML e física (cannon-es)
- Arena retangular (800×800 unidades) com chão e paredes
- Câmera em primeira pessoa (headless WebGL + fallback 2D) exposta via API REST (`GET /api/camera`)
- Sensores de proximidade frontal e traseiro (`GET /api/sensors`)
- MCP Server e Harness que operam o robô de forma agêntica

Atualmente, a arena contém apenas o robô, o chão e as quatro paredes. Isso faz com que a câmera do robô retorne imagens monótonas — apenas paredes e chão verde — o que limita drasticamente a utilidade da ferramenta de câmera para o loop agêntico do harness. O LLM não consegue "enxergar" nada de interessante para descrever ao usuário ou para se orientar no ambiente.

Esta tarefa adiciona objetos e itens na arena para que a função de câmera faça sentido, permitindo que o robô "veja" e "descreva" elementos distintos no ambiente.

## Requisitos Funcionais

### RF01 - Objetos Geométricos na Arena
A arena deve conter 4 a 6 objetos geométricos de tamanho médio (10–20 unidades), em cores distintas, posicionados em locais fixos pré-definidos.

**Regras:**
- Os objetos são: cubos, cones e esferas
- Cores distintas para fácil identificação visual: vermelho, azul, amarelo, verde, laranja, roxo
- Tamanho médio: cubos ~15×15×15, esferas raio ~10, cones raio base ~10 altura ~15
- Posições fixas pré-definidas dentro da arena (ex: (-150, -150), (150, -100), (-100, 150), (180, 180), (0, -180), (-180, 0))
- Os objetos permanecem nas mesmas posições após `POST /api/reset`
- Os objetos não podem ser coletados, removidos ou empurrados pelo robô
- Os objetos são puramente decorativos/pontos de referência visual

**Cenários de erro:**
- Objeto posicionado fora da arena ou sobreposto a parede: deve ser reposicionado automaticamente para dentro da área válida
- Objeto sobreposto ao robô na posição inicial (0,0): deve ser reposicionado para não obstruir o spawn

### RF02 - Objetos na Visualização 3D do Navegador
Os objetos devem ser renderizados na cena Three.js do navegador, visíveis na visualização 3D do simulador.

**Regras:**
- Os objetos devem lançar e receber sombras (`castShadow = true`, `receiveShadow = true`)
- Os objetos devem usar `MeshStandardMaterial` para consistência com o restante da cena
- Os objetos são adicionados à cena no momento da inicialização do `SimulatorEngine` ou `SimulatorCanvas`

### RF03 - Objetos no Renderer Headless WebGL 3D
Os objetos devem aparecer na imagem retornada pelo endpoint `GET /api/camera` quando o renderer headless opera em modo WebGL 3D.

**Regras:**
- A classe `HeadlessSceneRenderer` (modo WebGL) deve reconstruir os mesmos objetos na cena headless
- A geometria, cor e posição dos objetos no headless devem ser idênticas às do navegador
- Os objetos NÃO precisam ser reimplementados no renderer 2D top-down fallback (`render2DScene`)

**Cenários de erro:**
- Falha na inicialização do contexto WebGL: o fallback 2D continua funcionando sem objetos (comportamento aceitável)

### RF04 - Objetos Detectáveis pelos Sensores de Proximidade
Os sensores de proximidade (`GET /api/sensors`) devem reportar a distância até o objeto mais próximo (frente ou trás), não apenas até as paredes.

**Regras:**
- O cálculo geométrico de proximidade deve considerar tanto as paredes da arena quanto os objetos
- A distância reportada é a menor distância até qualquer obstáculo na direção do sensor (parede OU objeto)
- Formato de resposta permanece `{ frente: <float>, tras: <float> }` em centímetros
- Objetos são modelados como caixas delimitadoras (AABB) simplificadas para o cálculo de raycasting

**Cenários de erro:**
- Nenhum obstáculo no alcance: retornar valor máximo (400 cm) como já faz hoje

### RF05 - Colisão Física dos Objetos (cannon-es)
Os objetos devem ter corpos físicos no mundo cannon-es, impedindo que o robô os atravesse.

**Regras:**
- Cada objeto tem um `CANNON.Body` com massa 0 (estático) e forma geométrica correspondente (Box, Sphere)
- O robô colide com os objetos e é desviado/impedido de passar, assim como com as paredes
- Os objetos não se movem (massa = 0)
- Não há interação além da colisão (não coletáveis, não empurráveis)

**Cenários de erro:**
- Colisão mal configurada (objeto sem body físico): o robô atravessa o objeto visual

## Requisitos Não-Funcionais

- **RNF01**: O número de objetos (4–6) e suas posições devem ser facilmente configuráveis no código (array/constante), mas não precisam ser expostos via API REST
- **RNF02**: A renderização no navegador não deve degradar a performance abaixo de 60 FPS
- **RNF03**: O cálculo de proximidade no servidor (Node.js) deve permanecer síncrono e rápido (O(n) onde n = número de objetos, que é pequeno)

## Glossário / Definições

- **Objeto / Item**: Qualquer entidade geométrica estática na arena além do robô e das paredes (cubos, cones, esferas)
- **AABB (Axis-Aligned Bounding Box)**: Caixa delimitadora alinhada aos eixos, usada para simplificar o raycasting de proximidade contra objetos
- **Renderer headless**: Renderização 3D sem navegador, usada pela API `/api/camera` para gerar imagens via WebGL nativo (`gl`)
- **Modo 2D fallback**: Renderização top-down simplificada usada quando WebGL headless não está disponível
- **cannon-es**: Motor de física usado no navegador para colisões e movimentação do robô

## Premissas

- O simulador já possui câmera headless e sensores implementados (Fase 01 concluída)
- A arena tem tamanho fixo de 800×800 unidades (paredes em ±400, mas HALF_ARENA usado nos sensores é 200 — isto será verificado na fase técnica)
- O robô inicia no centro (0, 0)
- O número de objetos é pequeno (≤6), então performance não é uma preocupação
- O MCP Server e o Harness já estão funcionais; esta tarefa é uma evolução do simulador, não requer mudanças no MCP Server

## Fora de escopo

- Endpoint REST para listar/adicionar/remover objetos dinamicamente
- Objetos que aparecem no renderer 2D fallback
- Texturas complexas nos objetos (apenas cores sólidas)
- Objetos coletáveis, empurráveis ou com comportamento dinâmico
- Suporte a diferentes conjuntos de objetos (apenas um conjunto fixo)
- Mudanças no MCP Server, Harness ou tradutor
- Alteração do comportamento de movimentação LBML existente

## Cenarios de Aceite

### CA01 - Câmera mostra objetos na imagem
**Dado** que o simulador está rodando com o robô posicionado de forma que um objeto esteja à sua frente
**Quando** a ferramenta de câmera é acionada via `GET /api/camera` (modo WebGL)
**Então** a imagem retornada em base64 contém a representação do objeto (cor e forma visíveis)

### CA02 - Visualização 3D no navegador mostra objetos
**Dado** que o simulador está aberto no navegador
**Quando** o usuário observa a arena
**Então** os 4–6 objetos coloridos estão visíveis no chão, lançando sombras

### CA03 - Sensor de proximidade detecta objeto à frente
**Dado** que o robô está a 50 cm de um objeto à sua frente e a 200 cm da parede
**Quando** `GET /api/sensors` é chamado
**Então** o valor de `frente` retornado é ~50 cm (o objeto, não a parede)

### CA04 - Robô colide com objeto e não atravessa
**Dado** que existe um objeto no caminho do robô
**Quando** o robô recebe o comando LBML para andar em direção ao objeto
**Então** o robô para ou desliza ao lado do objeto, sem atravessá-lo

### CA05 - Renderer 2D fallback continua funcionando
**Dado** que o ambiente não suporta WebGL 2 headless
**Quando** `GET /api/camera` é chamado
**Então** a imagem 2D top-down é retornada normalmente (sem objetos, comportamento aceitável)

### CA06 - Reset preserva objetos
**Dado** que o robô se moveu e colidiu com objetos
**Quando** `POST /api/reset` é executado
**Então** o robô volta ao centro, e todos os objetos permanecem nas mesmas posições originais
