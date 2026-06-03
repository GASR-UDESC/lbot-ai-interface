import argparse
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
║    /help    - Mostra esta ajuda                   ║
║    /tools   - Lista ferramentas disponíveis       ║
║    /reset   - Limpa o histórico de conversa       ║
║    /history - Mostra o histórico de conversa      ║
║    /exit    - Encerra o harness                   ║
╚══════════════════════════════════════════════════╝
"""

HELP_TEXT = """
Comandos disponíveis:

  /help     Mostra esta ajuda
  /tools    Lista as ferramentas MCP disponíveis
  /reset    Limpa o histórico de conversa (o robô esquece tudo)
  /history  Mostra o histórico de mensagens da conversa
  /exit     Encerra o harness (também /quit ou Ctrl+D)

Você pode conversar com o robô em linguagem natural. O robô mantém
memória da conversa entre comandos. Exemplos:

  • "tire uma foto"
  • "me diga a distância até a parede"
  • "ande 30cm para frente"
  • "gira 180 graus, olha na câmera, se ver bola amarela anda 20cm pra direita"
  • "procure algo vermelho na sala"

O robô usará seus sensores, câmera e motores para responder da melhor
forma possível. Pressione Ctrl+C durante uma execução para interromper
o agente e voltar ao prompt.
"""


def _color(text: str, color: str) -> str:
    colors = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "gray": "\033[90m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def _print_event(event: str, data: dict) -> None:
    if event == "goal":
        print(f"  {_color('▶', 'cyan')} { _color('Objetivo:', 'bold')} {data.get('goal', '')}")
        print()
    elif event == "llm_request":
        step = data.get("step", 0)
        print(f"  {_color('─' * 50, 'gray')}")
        print(f"  {_color('▶', 'blue')} { _color(f'Passo {step}', 'bold')} – Requisição à IA")
        for msg in data.get("messages", []):
            role = msg.get("role", "?")
            content = msg.get("content", "")
            if role == "system":
                print(f"     {_color('sys:', 'gray')} {content[:120]}")
            elif role == "user":
                print(f"     {_color('user:', 'green')} {content[:200]}")
            elif role == "assistant":
                print(f"     {_color('assistant:', 'magenta')} {content[:200]}")
            elif role == "tool":
                print(f"     {_color('tool:', 'yellow')} {content[:200]}")
            else:
                print(f"     {_color(role + ':', 'gray')} {content[:200]}")
    elif event == "llm_request_retry":
        step = data.get("step", 0)
        reason = data.get("reason", "")
        print(f"     {_color('↻', 'yellow')} Passo {step}: tentando novamente – {reason}")
    elif event == "llm_response":
        step = data.get("step", 0)
        finish = data.get("finish_reason", "")
        content = data.get("content", "")
        tool_calls = data.get("tool_calls", [])
        print(f"  {_color('◀', 'blue')} { _color(f'Resposta da IA (passo {step})', 'bold')} – finish_reason={finish}")
        if content:
            print(f"     {_color('pensamento:', 'cyan')} {content.strip()}")
        if tool_calls:
            for tc in tool_calls:
                name = tc.get("name", "?")
                args = tc.get("arguments", "")
                print(f"     {_color('▸', 'yellow')} tool: { _color(name, 'bold')}({args})")
    elif event == "tool_call":
        step = data.get("step", 0)
        tool = data.get("tool", "?")
        args = data.get("arguments", {})
        print(f"  {_color('▶', 'yellow')} { _color(f'Passo {step}', 'bold')} – Executando: { _color(tool, 'bold')}({args})")
    elif event == "tool_result":
        step = data.get("step", 0)
        tool = data.get("tool", "?")
        result = data.get("result", "")
        print(f"  {_color('◀', 'yellow')} { _color(f'Resultado de {tool} (passo {step})', 'bold')}")
        print(f"     {result}")
    elif event == "final_answer":
        step = data.get("step", 0)
        content = data.get("content", "")
        print(f"  {_color('─' * 50, 'gray')}")
        print(f"  {_color('✓', 'green')} { _color(f'Resposta final (passo {step})', 'bold')}")
        print(f"     {content}")
        print()
    elif event == "error":
        step = data.get("step", 0)
        error = data.get("error", "")
        print(f"  {_color('✗', 'red')} { _color(f'Erro no passo {step}', 'bold')}: {error}")
    elif event == "cancelled":
        print(f"  {_color('✗', 'red')} { _color('Interrompido pelo usuário', 'bold')}")
    elif event == "max_steps_reached":
        max_steps = data.get("max_steps", 0)
        print(f"  {_color('⚠', 'yellow')} { _color(f'Máximo de passos atingido ({max_steps})', 'bold')}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lbot-harness",
        description="LBot Harness – Interface CLI para o robô E-Puck agêntico.",
    )
    parser.add_argument(
        "--show-thinking",
        action="store_true",
        default=True,
        dest="show_thinking",
        help="Mostra o raciocínio passo a passo da IA no terminal (padrão: ativado)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Não mostra o raciocínio, apenas 'Pensando...' e a resposta final",
    )
    return parser


def main():
    args = _build_parser().parse_args()
    show_thinking = not args.quiet and args.show_thinking
    asyncio.run(_async_main(show_thinking))


async def _async_main(show_thinking: bool):
    print(BANNER)
    print("Conectando ao corpo do robô...")

    try:
        async with MCPClient() as client:
            await _run_repl(client, show_thinking)
    except ConnectionError as e:
        print(f"\n  Erro: {e}")
        print("  Verifique se o MCP Server está disponível.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAté logo!")


async def _run_repl(client: MCPClient, show_thinking: bool):
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

    agent = ReActAgent(
        client,
        on_event=_print_event if show_thinking else None,
    )
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
            elif cmd == "/reset":
                agent.reset()
                print("Histórico limpo! O robô esqueceu tudo da conversa anterior.\n")
            elif cmd == "/history":
                summary = agent.history_summary
                if summary:
                    print(f"\nHistórico de conversa:\n{summary}\n")
                else:
                    print("\nNenhum histórico ainda.\n")
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

        if not show_thinking:
            print("\n🤖 Pensando...")
        try:
            running_task = asyncio.create_task(agent.run(user_input))
            result = await running_task
            if not show_thinking:
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
