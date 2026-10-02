# LBot: harness e core MCP

O Qwen escolhe ferramentas; habilidades executam movimentos e verificam resultados. O core depende de `LBotBackend`, não de objetos ou coordenadas privilegiadas do simulador. Um adapter físico futuro implementa câmera, sensores, execução confirmada e parada; pose absoluta é opcional.

## Executar localmente

No LM Studio, carregue Qwen3.5 4B com visão e habilite o servidor em `http://127.0.0.1:1234`. O identificador padrão é `qwen3.5-4b`. A integração envia `reasoning_effort: none`, validado neste runtime; o preflight rejeita um servidor que ainda produza raciocínio ou não interprete chamadas. Não use o modelo Base. O perfil testado é GGUF Q4_K_S e contexto de 8.192 tokens.

Inicie o simulador seguindo seu README. Depois, neste diretório:

```sh
uv sync --extra dev
export LBOT_LLM_MODEL=qwen3.5-4b
uv run lbot-harness
```

A configuração fica em variáveis de ambiente; `.env.example` documenta os padrões, mas não é carregado automaticamente. O checkpoint do tradutor deve existir em `2.treinamento-de-modelo/lbot-natural-language-controller/lbot-v7/lbot_translator_v7.pt`, ou em `LBOT_TRANSLATOR_MODEL`. O código do tradutor v7 permanece parte da dependência local.

Na inicialização o harness testa visão, uma ferramenta fictícia e continuação da conversa. Esse teste nunca movimenta o robô. `Ctrl+C` cancela o episódio e solicita parada; `/exit` encerra o terminal.

## Ferramentas

- `camera`: imagem frontal atual e metadados, sem pose absoluta.
- `proximity`: centímetros, validade e revisão da observação.
- `move`: frases concretas, por exemplo `ande 30 cm para frente` e `vire 90 graus para esquerda`; inclui tradutor neural, conferência de valores/direções, segmentação e confirmação.
- `search_object`: busca limitada com giros e deslocamentos verificados; não faz aproximação final e não prova ausência em toda a arena.
- `approach`: `target=object` com descrição, ou `target=front_obstacle`; distância padrão 50 cm. Bloqueios são relatados, sem desvio automático.
- `stop`: cancela habilidade e movimento.

Distância frontal é ao obstáculo mais próximo. O controlador não atribui essa medida a um objeto sem associação visual. O Qwen identifica alvos e seleciona regiões; OpenCV propõe regiões e acompanha um alvo já selecionado, sem veto por forma geométrica rígida.

Resultados diferenciam detecção, centralização e chegada. Um comando aceito não é um comando concluído. Timeout ou perda de resposta nunca causam repetição automática de movimento.

## Testes e avaliação

```sh
uv run pytest -q
```

O backend falso testa as habilidades sem pose absoluta, com atraso e falhas. O conjunto `evals/cases.json` tem 60 pedidos únicos, metade para desenvolvimento e metade reservada para aceitação. Os rótulos e estados diagnósticos não são enviados ao agente.

Para avaliar, execute uma instância exclusiva do simulador com `PORT=3003 LBOT_ENABLE_EVAL=1 npm run start`. Neste diretório:

```sh
PYTHONPATH=src uv run python evals/run.py --split development --output development
PYTHONPATH=src uv run python evals/run.py --split acceptance --output acceptance
```

O avaliador muda cenas e verifica o estado final independentemente da fala do modelo. Os cenários reservados não devem ser usados para ajustar o prompt. O endpoint de cenários é desativado por padrão e não é uma ferramenta MCP.

A busca tem orçamento próprio de 150 s e informa cobertura parcial quando necessário; uma busca negativa verifica o retorno à origem usando movimento relativo. Para o guia integrado e os contratos do futuro adapter físico, consulte `../IMPLEMENTACAO_HARNESS_SIMULADOR.md`.

Traces em `runs/` registram decisões, resultados, operações e uso/latência da inferência, inclusive percepção interna. Imagens e credenciais não são gravadas nesses logs. `evals/*/REPORT.md` relata resultados observados; as metas do plano não são declaradas atingidas automaticamente.

## Limitações explícitas

Esta versão não implementa navegação com desvios nem localização física. A associação de alvo com o feixe frontal usa a calibração câmera–sensor e a região visual do alvo; sem calibração, usa confirmação visual conservadora. O contrato prevê um adapter físico, mas ele ainda não está implementado. Latência e consumo do Qwen precisam ser medidos no hardware de cada execução.
