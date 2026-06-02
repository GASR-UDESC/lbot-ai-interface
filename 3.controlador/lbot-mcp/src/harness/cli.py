import asyncio
import logging
import signal
import sys

from .agent import ReActAgent
from .mcp_client import MCPClient, ConnectionError

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

BANNER = """
╔══════════════════════════════════════════════════╗
║       LBot Harness - Seu robô E-Puck agêntico   ║
║                                                  ║
║  Conecte-se ao seu robô e explore o mundo!       ║
║  Comandos especiais:                             ║
║    /help   - Mostra esta ajuda                   ║
║    /tools  - Lista ferramentas disponíveis       ║
║    /exit   - Encerra o harness                   ║
╚══════════════════════════════════════════════════╝
"""

HELP_TEXT = """
Comandos disponíveis:

  /help     Mostra esta ajuda
  /tools    Lista as ferramentas MCP disponíveis
  /exit     Encerra o harness (também /quit ou Ctrl+D)

Você pode conversar com o robô em linguagem natural. Exemplos:

  • "tire uma foto"
  • "me diga a distância até a parede"
  • "ande 30cm para frente"
  • "explore a sala e me diga o que você vê"

O robô usará seus sensores, câmera e motores para responder da melhor
forma possível. Pressione Ctrl+C durante uma execução para interromper
o agente e voltar ao prompt.
"""


def main():
    asyncio.run(_async_main())


async def _async_main():
    print(BANNER)
    print("Conectando ao corpo do robô...")

    try:
        async with MCPClient() as client:
            await _run_repl(client)
    except ConnectionError as e:
        print(f"\n  Erro: {e}")
        print("  Verifique se o MCP Server está disponível.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAté logo!")


async def _run_repl(client: MCPClient):
    try:
        tools = await client.list_tools()
    except Exception:
        tools = []

    if tools:
        print("\nFerramentas disponíveis:")
        for t in tools:
            print(f"  • {t['name']}: {t['description'][:80]}")
    else:
        print("\nNenhuma ferramenta disponível.")

    agent = ReActAgent(client)
    print("\nPronto! Digite seu comando ou /help para ajuda.\n")

    loop = asyncio.get_running_loop()
    running_task: asyncio.Task | None = None

    def _sigint_handler():
        if running_task and not running_task.done():
            if agent:
                agent.cancel()
            print("\n  Interrompido.")
        else:
            print("\n  Use /exit para sair.")

    try:
        loop.add_signal_handler(signal.SIGINT, _sigint_handler)
    except NotImplementedError:
        pass

    while True:
        try:
            user_input = await _get_input()
        except EOFError:
            print("\nAté logo!")
            break
        except KeyboardInterrupt:
            print("\nAté logo!")
            break

        user_input = user_input.strip()
        if not user_input:
            continue

        if user_input.startswith("/"):
            cmd = user_input.lower()
            if cmd in ("/exit", "/quit", "/q"):
                print("Até logo!")
                break
            elif cmd == "/help":
                print(HELP_TEXT)
            elif cmd == "/tools":
                try:
                    tools = await client.list_tools()
                    print("\nFerramentas disponíveis:")
                    for t in tools:
                        print(f"  • {t['name']}: {t['description']}")
                    print()
                except Exception as e:
                    print(f"Erro ao listar ferramentas: {e}")
            else:
                print(f"Comando desconhecido: {user_input}. Use /help para ajuda.")
            continue

        print(f"\n🤖 Pensando...")
        try:
            running_task = asyncio.create_task(agent.run(user_input))
            result = await running_task
            print(f"\n🤖 {result}\n")
        except asyncio.CancelledError:
            print("\n  Interrompido.")
        except Exception as e:
            print(f"\n  Erro: {e}\n")
        finally:
            running_task = None


async def _get_input() -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: input("🤖 > "))
