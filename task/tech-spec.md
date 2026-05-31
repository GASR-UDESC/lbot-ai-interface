# Plano Tecnico: Melhorias no Level Design, Fisica e UI do lbot-datagen

## Visao Geral

Implementar redesign de niveis com dificuldade progressiva (paredes horizontais com gaps obrigatorios), corrigir fisica de colisao das arena walls via ajuste no sistema ray-march existente, adicionar timer global (runStartTime), redesenhar UI com estetica gaming moderno (cores por nivel, sem glassmorphism), e criar testes unitarios para os services criticos.

A abordagem privilegia mudancas incrementais e testáveis. Cada fase entrega valor independente e pode ser validada isoladamente.

## Modulos Envolvidos

- **level-config.model.ts**: Redesign completo dos 5 LEVEL_CONFIGS com obstaculos que bloqueiam largura total da arena
- **robo-simulator.ts**: Remocao do botao "Novo Desafio" e metodo generateNewLevel()
- **physics.service.ts**: Ajuste em isValidPosition() para checar arena walls; aumento da altura das paredes
- **game-state.service.ts**: Adicao de runStartTime para timer global que nao para entre niveis
- **game.page.ts / game.page.html / game.page.css**: Layout grid com padding/gap, HUD redesenhado
- **robo-simulator.css**: UI gaming moderno - cores vivas por nivel, sem gradientes/glow excessivos

## Arquivos Impactados

### Novos
- `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.spec.ts` - Testes unitarios de colisao
- `lbot-datagen/lbot-datagen-frontend/src/app/services/game-state.service.spec.ts` - Testes do timer global
- `lbot-datagen/lbot-datagen-frontend/src/app/services/level-config.service.spec.ts` - Validacao dos niveis

### Alterados
- `lbot-datagen/lbot-datagen-frontend/src/app/models/level-config.model.ts` - Redesign dos 5 niveis com obstaculos full-width
- `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.ts` - Remover generateNewLevel(), botao "Novo Desafio" e metodos auxiliares
- `lbot-datagen/lbot-datagen-frontend/src/app/components/robo-simulator/robo-simulator.css` - UI gaming: cores dinamicas, sem glassmorphism
- `lbot-datagen/lbot-datagen-frontend/src/app/services/physics.service.ts` - Arena walls na checagem de colisao, altura das paredes 30+ unidades
- `lbot-datagen/lbot-datagen-frontend/src/app/services/game-state.service.ts` - runStartTime signal, getGlobalElapsedMs()
- `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.ts` - Timer global no display
- `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.html` - Layout grid, remocao de HUD conflitantes
- `lbot-datagen/lbot-datagen-frontend/src/app/pages/game/game.page.css` - Grid layout com gap:24px, padding:24px, border-radius
- `lbot-datagen/lbot-datagen-frontend/src/app/services/arena-builder.service.ts` - Aumento da wallHeight para 30

## Decisoes Tecnicas

| Decisao | Opcao escolhida | Justificativa |
|---------|-----------------|---------------|
| Modelo de obstaculos niveis 1-2 | Paredes horizontais com gap | Forca desvio lateral sem complexidade de labirinto. Facil de entender para niveis iniciais |
| Sistema de colisao | Manter ray-march + ajustar | Menos risco de quebrar o movimento existente. Sistema ja funciona para obstaculos, apenas faltam as arena walls |
| Paleta de cores UI | Cores vivas por nivel (do tema) | Reforça identidade visual de cada nivel. Usa dados ja existentes no ThemeConfig |
| Timer global | Adicionar runStartTime no GameStateService | Signal unico que marca inicio da run. Display = Date.now() - runStartTime. Simples e sem drift |
| Remocao generateNewLevel | Remover botao + metodo inteiro | O modo controle (showGoals=false) nunca usa. Simplifica o componente |
| Layout game page | Grid + padding igual controls page | Consistencia com pattern ja existente no projeto. Gap 24px + border-radius 16px |
| Rampas niveis 4-5 | Box inclinado com rampAngle | Sistema ja suportado. Basta posicionar rampa como unico acesso a area elevada no level design |
| Responsividade | 768px vertical, >768 lateral | Mantem o breakpoint existente funcional enquanto garante experiencia boa em >= 1024px |
| Testes | Unit tests nos services (Jasmine/Karma) | Cobre logica critica sem overhead de integration tests. Framework ja configurado |

## Dependencias entre Fases

- Fase 01 (Level Design) -> Fase 02 (Fisica) - Os niveis redesenhados precisam estar la para testar que a fisica impede contorno
- Fase 02 (Fisica) -> Fase 03 (Timer) - Timer so faz sentido quando o jogo e jogavel com colisoes corretas
- Fase 03 (Timer) -> Fase 04 (UI) - A UI precisa exibir o timer global corretamente
- Fase 04 (UI) -> Fase 05 (Testes) - Testes validam o comportamento final de todos os modulos

## Mapa de Fases

| Fase | Descricao | Modulo |
|------|-----------|--------|
| 01 | Redesign Level Design + Remocao "Novo Desafio" | level-config.model, robo-simulator |
| 02 | Fisica: arena walls no ray-march + altura paredes | physics.service, arena-builder |
| 03 | Timer Global (runStartTime) | game-state.service, game.page |
| 04 | UI/Layout Gaming Moderno | game.page.css, robo-simulator.css, game.page.html |
| 05 | Testes Unitarios | *.spec.ts (physics, game-state, level-config) |
