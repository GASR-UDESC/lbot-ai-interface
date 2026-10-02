# Resultados da implementação local

Execuções em 1–2 de outubro de 2026, Apple M4 com 16 GB, LM Studio, Qwen3.5 4B GGUF Q4_K_S e contexto de 8.192 tokens. Perfil e hash dos fontes: [runtime-local.json](runtime-local.json). Não houve treinamento ou troca do modelo Qwen durante a implementação.

O servidor executa a física e renderiza a câmera em Chromium. Os resultados abaixo foram obtidos com o modelo local real, sem uma aba do usuário controlando a simulação. Os rótulos, a pose absoluta e os objetos internos dos cenários são usados pelo avaliador e não são enviados ao agente.

## Evidência principal

| Execução | Resultado | Natureza |
|---|---:|---|
| Desenvolvimento | 30/30 | Conjunto disponível para diagnóstico |
| Primeira aceitação | 27/30 | Primeira exposição aos pedidos reservados |
| Correção do orçamento, antes do retorno corrigido | 28/30 | Regressão; duas buscas não retornaram corretamente |
| Aceitação final | **30/30** | Regressão final nos mesmos pedidos, com retorno e sensores verificados |
| Casos adicionais | **4/4** | Esfera azul, cone laranja, alvo parcialmente visível e oclusão do feixe frontal |

Os 60 pedidos principais têm dez casos por categoria: conversa, observação, sensores, movimentos/sequências, busca e aproximação. As últimas execuções correspondentes a cada caso passaram: 30 de desenvolvimento e 30 de aceitação final. Isso **não equivale a 60 testes independentes sobre uma versão final congelada**: o desenvolvimento ocorreu antes de algumas correções, e a aceitação foi repetida após revelar falhas.

Resultados completos: [development/results.json](development/results.json), [acceptance/results.json](acceptance/results.json), [acceptance-budget/results.json](acceptance-budget/results.json), [acceptance-final/results.json](acceptance-final/results.json) e [stress/results.json](stress/results.json). Métricas verificadas: [verified-metrics.json](verified-metrics.json).

## Verificação independente e desempenho

| Medida | Resultado observado |
|---|---:|
| Escolha de ferramenta nos 60 pedidos principais | 60/60 |
| Argumentos inválidos nesses episódios | 0 |
| Movimentos e sequências em espaço livre | 10/10, incluindo giro acumulado de 360° |
| Erro de pose dos movimentos | Menor que 0,01 cm e 0,01° no motor idealizado |
| Aproximações acessíveis | 8/8, erro máximo de 5 cm |
| Aproximações com bloqueio frontal próximo, versão final | 2/2 interrompidas antes de explorar |
| Registros de comando terminais auditados na aceitação final | 126 |
| Colisões nesses registros | 0 |
| Episódios finais com movimento ainda ativo | 0 |
| Tokens de entrada máximos observados no conjunto principal | 2.255 |
| Latência de inferência na aceitação final, p50 / p95 | 4,10 s / 5,37 s |
| Latência de episódio na aceitação final, p50 / p95 | 4,88 s / 148,45 s |
| Inferências na aceitação final | 124: 57 do harness e 67 da percepção interna |
| Câmera aquecida, 30 capturas, p50 / p95 | 20,10 ms / 26,75 ms |
| Parada por HTTP, 20 comandos em execução, p50 / p95 | 0,49 ms / 0,86 ms |

A aproximação foi conferida pela posição final e pela geometria do cenário, independentemente da distância declarada pela ferramenta. Leituras frontais/traseiras foram comparadas com valores esperados. Nas buscas negativas, o avaliador verifica retorno à posição e orientação de início; orientação é comparada módulo 360°, enquanto o teste de giro completo de `move` verifica a rotação acumulada.

Os alvos ausentes não produziram prova de ausência em toda a arena. A busca azul realizou 26 observações; a busca da esfera roxa realizou 25. Ambas encerraram pelo orçamento, informaram `search_complete=false` e voltaram à origem. Levaram 148,62 s e 148,45 s. Essa latência é uma limitação prática relevante: o custo de várias inferências visuais domina a busca negativa.

O benchmark de câmera/parada usa outra instância e inclui o transporte HTTP em loopback. A câmera já estava aquecida. Outras cargas locais não são controladas; esses números não representam inicialização fria nem o tempo total de uma tarefa com o Qwen. Procedimento reproduzível: [benchmark_simulator.py](benchmark_simulator.py), dados: [simulator-benchmark.json](simulator-benchmark.json).

Uma amostra do processo do modelo mostrou RSS de aproximadamente 3,18 GB, em repouso. RSS não mede toda a memória compartilhada/Metal, e não foi registrado um pico de memória de todos os componentes. Energia, temperatura e uso da GPU não foram medidos. `process_max_rss` nos episódios corresponde ao avaliador Python, não ao modelo ou ao servidor MCP.

## Testes automatizados

**70 testes Python e 9 testes Node aprovados.** TypeScript, build de produção, Ruff, mypy e `git diff --check` também passaram. A interface foi inspecionada em Chromium: câmera visível, botão de parada disponível e nenhum erro de página.

Os testes exercitam conclusão efetiva, movimentos/giros, colisão e execução parcial, idempotência, concorrência, cancelamento, reset, sessão antiga entre observação e ação, falhas de câmera/sensor, tradução divergente, protocolo multimodal, argumentos inválidos, cancelamento durante inferência/busca, resposta de execução perdida e limite de contexto. O teste HTTP abre duas abas, fecha ambas durante movimento e verifica a conclusão no servidor. Outro teste remove deliberadamente o acesso ao Chromium e confirma HTTP 503 com `camera_unavailable`, sem imagem substituta.

Um segundo backend falso acompanha movimento relativo, introduz atraso e mantém `get_state()` sem pose absoluta. Ele verificou que uma varredura parcial restaura o rumo antes de recuar. No simulador real, as buscas negativas finais também confirmaram esse retorno.

## Falhas encontradas e corrigidas

1. **Raciocínio permanecia ativo:** a medição inicial aceitou ferramentas/imagens, mas `enable_thinking=false` não desativou raciocínio neste runtime. `reasoning_effort=none` resolveu o caso; o preflight passou a verificar a compatibilidade.
2. **Associação entre alvo e sensor:** depender apenas de uma indicação booleana do modelo bloqueava aproximações válidas. A associação utiliza parâmetros calibrados e a região visual; uma oclusão azul sobre o feixe permaneceu bloqueada no teste adicional.
3. **Busca ausente ultrapassava 180 s:** até 40 inferências visuais excediam o limite da habilidade. A busca ganhou orçamento próprio, reserva para retorno e relato explícito de cobertura parcial. Timeout de inferência continua sendo erro.
4. **Busca de aproximação podia contornar um bloqueio próximo:** a verificação inicial de proximidade agora impede essa exploração dentro da margem mínima.
5. **Retorno durante varredura parcial usava o rumo errado:** restaurar a orientação relativa do avanço antes de recuar corrigiu o retorno, sem consultar pose absoluta no core.
6. **Chamadas múltiplas podiam continuar após falha:** o harness responde todos os identificadores, mas cancela as ações seguintes; `busy` e sessão obsoleta não solicitam parada de outra operação.

A configuração dos pedidos de aceitação e os prompts de controle não foram ajustados para decorar os casos que falharam. As correções ocorreram nas camadas de execução, orçamento, percepção e segurança. O histórico original permanece disponível, inclusive o comportamento que chegou ao alvo apesar do bloqueio inicial.

## Limites da conclusão

O sistema funcionou nos cenários executados, no hardware local solicitado. As metas de 95–99% foram alcançadas numericamente nessa pequena amostra, mas dez casos por categoria **não sustentam uma estimativa estatística de 99% de confiabilidade geral**. A primeira aceitação foi 90%; a execução final é uma regressão após correções, não um novo conjunto intocado.

A física é idealizada e os objetos são simples. Ainda faltam testes extensos com iluminação variável, múltiplos objetos semelhantes, oclusões da mesma cor, ruído, escorregamento e hardware real. Não foram implementados planejador de desvios, adapter físico ou implantação em Raspberry Pi. O contrato para outro backend está implementado e exercitado por fakes; a segurança no robô real depende também de encoders, watchdog e parada no próprio controlador.

Para a dissertação, o próximo conjunto reservado deve ser maior, conter novas cenas e ser congelado antes dos ajustes. Repetições, sementes, dispersão de latência e intervalos de confiança devem acompanhar as médias. A contribuição pode ser avaliada comparando harness com habilidades verificadas contra controle direto pelo modelo, usando os mesmos cenários e o mesmo Qwen.
