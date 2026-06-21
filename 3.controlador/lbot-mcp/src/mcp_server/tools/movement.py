import httpx

from ..server import mcp
from ..context import get_backend, get_translator
from ..translator import TranslationError


@mcp.tool()
async def move(command: str) -> str:
    """ Executa um movimento do robô. O comando deve ser descrito em linguagem natural (português), mas sempre representando ações físicas concretas e observáveis do robô. Os movimentos devem indicar explicitamente deslocamentos, rotações ou outras ações físicas necessárias para executar a tarefa. Sempre que aplicável, utilize valores mensuráveis e específicos (por exemplo, distâncias em centímetros e rotações em graus). O comando é sempre relativo à posição e orientação atual do robô. Exemplos: - 'ande 30 cm para frente' - 'vire 90 graus para a direita' - 'ande 15 cm para frente, depois vire 180 graus para a direita' - 'ande 20 cm para frente e gire 15 graus para a esquerda' Evite descrições vagas ou subjetivas, como: - 'avance um pouco' - 'gire levemente para a esquerda' - 'chegue mais perto' - 'vá naquela direção' Quando o usuário fornecer um objetivo de alto nível, uma trajetória abstrata ou um padrão geométrico (por exemplo, 'vá até a porta', 'ande em zigue-zague', 'faça um círculo', 'desenhe um quadrado', 'faça um X' ou 'contorne a mesa'), o modelo deve primeiro convertê-lo em uma sequência explícita de movimentos concretos, específicos e mensuráveis antes de utilizar esta ferramenta. A ferramenta não interpreta objetivos, formas ou trajetórias abstratas; ela executa apenas a sequência detalhada de movimentos gerada pelo modelo. """
    try:
        translator = get_translator()
        lbml = translator.translate(command)
    except TranslationError:
        return (
            "Erro: não entendi o comando. Use frases como "
            "'ande 30cm para frente', 'vire 90 graus para direita'."
        )

    try:
        backend = get_backend()
        result = await backend.execute_lbml(lbml, wait=True)

        if result.get("accepted"):
            return f"Comando executado: {command}"
        else:
            error_msg = result.get("error", "falha na execucao")
            return f"Erro: falha na execucao — {error_msg}"

    except RuntimeError as e:
        error_str = str(e)
        if "409" in error_str:
            return "Erro: o simulador nao esta conectado. Abra o simulador no navegador para executar movimentos."
        return f"Erro: falha na execucao — {e}"
    except httpx.TimeoutException:
        return "Erro: timeout ao executar movimento."
    except Exception as e:
        return f"Erro: falha na execucao — {e}"
