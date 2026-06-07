# Especificacao de Negocio: Busca de Objetos na Arena

## Contexto

O robô LBot hoje consegue capturar imagens da câmera (`camera()`), medir distâncias com sensores de proximidade (`proximity()`) e executar movimentos via LBML (`move()`). Porém, não existe funcionalidade autônoma de busca de objetos. O usuário precisa manualmente orquestrar rotações, capturas e avanços para encontrar algo.

Esta feature adiciona um novo MCP tool `search_object` que automatiza o fluxo completo de busca: varredura da arena com OpenCV, centralização do objeto no frame e aproximação progressiva até o alvo. A LLM coordena o fluxo em alto nível (interpreta o pedido do usuário, chama o tool, comunica resultados), mas **não processa imagens nem calcula ângulos** — isso fica a cargo do OpenCV e de cálculos matemáticos no servidor.

## Requisitos Funcionais

### RF01 — Tool `search_object` (End-to-End)

O MCP server expõe um novo tool `search_object(description: str)` que executa o ciclo completo de busca. A LLM chama este tool quando o usuário pede para encontrar algo na arena.

**Regras:**
- O parâmetro `description` é texto livre com a descrição do objeto alvo (ex: "cubo vermelho", "esfera azul", "cone", "cubo")
- A LLM é responsável por extrair tipo e/ou cor da fala do usuário e passar como `description`
- O tool retorna um dicionário com `status` ("found" | "not_found"), `object_type`, `object_color` (se detectado), `bounding_box` (se detectado), `final_distance_cm` (se aproximou), e `steps_taken` (resumo das etapas executadas)
- O tool executa internamente 4 fases: varredura → centralização → aproximação → resultado
- A LLM recebe o retorno e elabora a mensagem final para o usuário em linguagem natural

**Cenários de erro:**
- `description` vazia ou inválida: tool retorna erro de validação
- Backend do simulador indisponível: tool propaga o erro de conexão
- Câmera indisponível: tool retorna erro "camera unavailable"

### RF02 — Fase 1: Varredura (Scan)

O robô gira 360° em 4 passos de 90° para a esquerda, capturando um frame a cada rotação e processando com OpenCV para detectar o objeto alvo.

**Regras:**
- O robô começa na orientação atual (rotação 0° relativa)
- A cada iteração: captura frame → processa OpenCV → se detectado, interrompe a varredura e avança para centralização
- Se o objeto for detectado, registra em qual ângulo acumulado (0°, 90°, 180° ou 270°) foi encontrado
- Após cada comando `R90L;`, aguarda 2 segundos fixos para o movimento completar antes de capturar a câmera
- Se após as 4 rotações (0°, 90°, 180°, 270°) nenhum objeto for detectado, o tool retorna `status: "not_found"` e a LLM informa o usuário
- Se houver múltiplos objetos do mesmo tipo/cor no frame, seleciona o de maior bounding box (mais próximo)

**Cenários de erro:**
- Nenhum objeto detectado após 360°: tool retorna `not_found`
- Erro ao rotacionar (LBML inválido ou backend falhou): tool aborta e retorna erro
- Timeout na captura da câmera (5s): pula a iteração atual e continua para a próxima rotação

### RF03 — Fase 2: Detecção OpenCV

A detecção de objetos usa exclusivamente OpenCV, sem envolvimento da LLM. O tipo de detector depende do objeto buscado.

**Regras:**
- **Esferas**: `cv2.HoughCircles` sobre o frame (em escala de cinza ou com blur prévio)
- **Cubos**: `cv2.approxPolyDP` sobre contornos — busca contornos com aproximadamente 4 vértices (quadriláteros)
- **Cones**: `cv2.approxPolyDP` sobre contornos — busca contornos com aproximadamente 3 vértices (triângulos)
- **Filtro por cor**: se a LLM especificar uma cor no `description`, aplica-se máscara HSV antes da detecção de forma. O tool possui um dicionário interno de faixas HSV:
  - `vermelho`: lower=[0,100,100], upper=[10,255,255] + lower=[160,100,100], upper=[180,255,255]
  - `azul`: lower=[100,100,100], upper=[130,255,255]
  - `verde`: lower=[40,100,100], upper=[80,255,255]
  - `amarelo`: lower=[20,100,100], upper=[35,255,255]
  - `laranja`: lower=[10,100,100], upper=[25,255,255]
  - `roxo`: lower=[130,100,100], upper=[160,255,255]
  - Sem cor especificada: detecta por forma sem máscara HSV
- **Múltiplos matches**: se houver mais de um objeto do mesmo tipo no frame (ex: dois cubos), seleciona o de maior área de bounding box (proxy de proximidade)
- O resultado da detecção é o centro do bounding box `(cx, cy)` do objeto selecionado

**Cenários de erro:**
- Frame muito escuro ou claro que impeça detecção: tenta equalização de histograma antes de detectar
- Objeto parcialmente ocluído (ex: atrás de outro): pode não ser detectado — isso é esperado. O robô seguirá para a próxima rotação

### RF04 — Fase 3: Centralização

Com o objeto detectado, calcula-se quantos graus o robô precisa girar para centralizá-lo no frame. O cálculo é puramente matemático, sem LLM.

**Regras:**
- O cálculo usa aproximação por FOV (câmera não calibrada):
  - `erro_x = cx - (largura_frame / 2)`
  - `graus = (erro_x / largura_frame) * fov_horizontal`
  - `fov_horizontal = 100` (FOV da PerspectiveCamera do simulador)
  - Sinal: positivo = girar para direita, negativo = girar para esquerda
- O valor de `graus` é enviado diretamente como comando LBML `R{graus}{L|R};`
- A LLM **não participa** do cálculo de graus
- Limite de 5 tentativas de centralização. Se após 5 ajustes o objeto não estiver dentro do threshold, considera falha
- O threshold de centralização é `|erro_x| < 64px` (10% da largura do frame 640px)

**Cenários de erro:**
- Excedeu 5 tentativas sem centralizar: retorna `not_found` com motivo "could not center"
- Objeto detectado mas `erro_x` calculado resulta em rotação menor que 1°: considera centralizado (evita micro-ajustes)

### RF05 — Fase 4: Aproximação

Com o objeto centralizado, o robô avança em passos progressivamente menores, validando visualmente a centralização a cada passo.

**Regras:**
- Passos planejados: 100cm → 50cm → 20cm
- Passos são **adaptativos**: se `distância_do_sensor < passo_planejado`, o passo é reduzido para `distância_do_sensor / 2`
  - Ex: sensor=80cm e passo planejado=100cm → anda 40cm
- Critério de parada: sensor de distância frontal ≤ 50cm
- A cada avanço:
  1. Executa comando `D{passo}F;` (deslocamento frontal)
  2. Aguarda 2 segundos para o movimento completar
  3. Captura frame e re-valida com OpenCV que o objeto ainda está visível e centralizado (`|erro_x| < 64px`)
  4. Se saiu do threshold: volta ao passo RF04 (centralização) ANTES de continuar avançando
  5. Lê sensor de proximidade frontal
- Se o sensor retornar "sem obstáculo (>400cm)" mas o OpenCV detecta o objeto: **reporta distância excessiva** (objeto está muito longe para aproximação segura)
- Limite máximo de 10 passos de avanço (somando todas as tentativas)
- O sensor frontal mede o obstáculo mais próximo na direção do robô. Como o objeto está centralizado na câmera, assume-se que a leitura do sensor é a distância até o objeto-alvo (não uma parede atrás dele)

**Cenários de erro:**
- Perda de tracking durante aproximação (OpenCV não detecta mais o objeto): volta para RF02 (re-varredura completa). Máximo 2 re-varreduras totais. Se falhar em ambas, retorna `not_found`
- Sensor frontal detecta obstáculo a < 20cm antes de atingir o critério de parada (50cm): aborta aproximação para evitar colisão, retorna `not_found` com "obstacle too close"
- Excedeu 10 passos sem atingir distância ≤ 50cm: retorna `not_found` com "max approach steps exceeded"

### RF06 — Comunicação de Resultados

Após o tool `search_object` concluir (sucesso ou falha), a LLM comunica o resultado ao usuário.

**Regras:**
- **Sucesso**: LLM informa que encontrou o objeto, qual era (tipo + cor), e que está próximo (≈50cm). Ex: "Encontrei o cubo vermelho! Estou a aproximadamente 50cm dele."
- **Não encontrado**: LLM informa que não encontrou o objeto na arena. Ex: "Não encontrei o cubo vermelho. A arena parece estar vazia ou o objeto não está visível."
- **Falha técnica**: LLM reporta o tipo de falha (câmera indisponível, erro de movimento, etc.)
- A LLM NÃO comunica detalhes técnicos (pixels, graus, coordenadas) a menos que o usuário peça

## Requisitos Não-Funcionais

- **Latência**: A detecção OpenCV deve processar um frame 640x480 em < 500ms
- **Precisão**: A centralização deve posicionar o objeto dentro de 10% do centro do frame (64px) em no máximo 5 iterações
- **Segurança**: O robô não deve colidir com obstáculos. Distância mínima de segurança: 20cm do sensor
- **OpenCV**: Deve ser adicionado como dependência no `pyproject.toml` (`opencv-python-headless`)

## Glossario / Definicoes

- **LBML**: LBot Markup Language — formato de comandos de movimento (`D<cm><F|B|L|R>;` para deslocamento, `R<graus><L|R>;` para rotação)
- **FOV**: Field of View — ângulo de visão horizontal da câmera (100° no simulador)
- **Threshold de centralização**: margem em pixels a partir do centro do frame onde o objeto é considerado "centralizado" (64px)
- **Passo adaptativo**: redução do passo de avanço quando o sensor indica distância menor que a planejada
- **Bounding box**: retângulo que envolve o objeto detectado, definido por (x, y, width, height). O centro é (cx, cy)

## Premissas

- A câmera do simulador retorna frames 640x480 em base64 PNG (comportamento atual mantido)
- O FOV horizontal da câmera é 100° (valor fixo do `PerspectiveCamera` no Three.js)
- A câmera NÃO é calibrada com `cv2.calibrateCamera`. Usa-se aproximação por FOV para converter pixels em graus
- Os objetos da arena são opacos e de cores sólidas (sem texturas), o que favorece detecção por forma e máscara HSV
- O sensor de proximidade mede a distância até o obstáculo mais próximo na direção frontal do robô
- O robô começa a busca da orientação atual. Não se reposiciona antes de iniciar
- O simulador está rodando e acessível via HTTP (backend `SimulatorBackend`)
- OpenCV será instalado como `opencv-python-headless` (sem dependências GUI)

## Fora de escopo

- Calibração de câmera com `cv2.calibrateCamera` e uso de `camera_matrix` para cálculo de graus (usar apenas aproximação FOV)
- Navegação com desvio de obstáculos (path planning). O robô só avança em linha reta na direção do objeto
- Busca com movimentação lateral ou traseira. Apenas rotação + avanço frontal
- Detecção de objetos atrás de outros objetos (oclusão total)
- Suporte a backends reais (hardware físico). Apenas o `SimulatorBackend` é suportado nesta iteração
- Persistência ou histórico de buscas anteriores

## Cenarios de Aceite

### CA01 — Busca bem-sucedida: objeto visível na primeira orientação
**Dado** que há um cubo vermelho na arena, visível na orientação atual do robô
**Quando** o usuário pede "ache o cubo vermelho"
**Então** o robô detecta o cubo no primeiro frame, centraliza (≤ 5 ajustes), avança em passos adaptativos até ≈50cm, e a LLM informa "Encontrei o cubo vermelho! Estou próximo dele."

### CA02 — Busca bem-sucedida: objeto encontrado após rotação
**Dado** que há uma esfera azul na arena, fora do campo de visão atual (ex: atrás do robô)
**Quando** o usuário pede "ache a esfera azul"
**Então** o robô rotaciona e detecta a esfera na 2ª ou 3ª rotação (após 90° ou 180°), centraliza, aproxima, e informa sucesso

### CA03 — Objeto não encontrado (arena sem o objeto)
**Dado** que a arena não contém cones
**Quando** o usuário pede "ache o cone laranja"
**Então** o robô faz a varredura completa de 360° (4 rotações), não detecta nada, e a LLM informa "Não encontrei o cone laranja"

### CA04 — Objeto não encontrado (arena vazia)
**Dado** que a arena está vazia (sem objetos)
**Quando** o usuário pede "ache o cubo"
**Então** o robô faz a varredura completa, não detecta nada, e a LLM informa que não encontrou

### CA05 — Múltiplos objetos do mesmo tipo: seleciona o mais próximo
**Dado** que há dois cubos vermelhos na arena (um a 80cm, outro a 150cm), ambos no frame
**Quando** o usuário pede "ache o cubo vermelho"
**Então** o OpenCV detecta ambos e seleciona o de maior bounding box (mais próximo) para centralizar e aproximar

### CA06 — Centralização converge em múltiplos ajustes
**Dado** que o objeto está a 150px do centro do frame (fora do threshold de 64px)
**Quando** o robô detecta o objeto e inicia a centralização
**Então** o robô calcula os graus, rotaciona, reavalia, e converge para dentro do threshold em no máximo 5 iterações

### CA07 — Aproximação com passos adaptativos
**Dado** que o objeto está centralizado e o sensor indica 80cm
**Quando** o robô inicia a aproximação (passo planejado: 100cm)
**Então** o passo é reduzido para 40cm (80/2), o robô avança, re-valida centralização, lê o sensor novamente e continua até ≤ 50cm

### CA08 — Perda de tracking durante aproximação
**Dado** que o robô está se aproximando do objeto, mas após um avanço o OpenCV não detecta mais o objeto
**Quando** o robô re-valida o frame após o avanço
**Então** volta para a fase de varredura (360°), tenta reencontrar. Se encontrar, retoma centralização e aproximação. Se falhar em 2 re-varreduras, retorna `not_found`

### CA09 — Objeto visível mas muito longe (>400cm do sensor)
**Dado** que o OpenCV detecta o objeto, mas o sensor de proximidade retorna "sem obstáculo (>400cm)"
**Quando** o robô tenta iniciar a aproximação
**Então** o tool retorna "object too far" e a LLM informa que o objeto está muito distante para aproximação segura

### CA10 — Limite de iterações de centralização excedido
**Dado** que o objeto foi detectado, mas após 5 ajustes de rotação ainda está fora do threshold de 64px
**Quando** o robô atinge o limite de 5 tentativas
**Então** o tool retorna `not_found` com motivo "could not center"

### CA11 — Limite de passos de aproximação excedido
**Dado** que o robô avança repetidamente mas o sensor nunca chega a ≤ 50cm (ex: objeto recuando ou erro de medição)
**Quando** o robô atinge 10 passos de avanço
**Então** o tool retorna `not_found` com motivo "max approach steps exceeded"

### CA12 — Busca de cone
**Dado** que há um cone laranja na arena
**Quando** o usuário pede "ache o cone laranja"
**Então** o OpenCV detecta o cone usando approxPolyDP com ~3 vértices (forma triangular), centraliza e aproxima até ≈50cm
