import argparse
import asyncio
import logging
import signal
import sys

from .agent import ReActAgent
from .mcp_client import MCPClient, ConnectionError

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", stream=sys.stderr)


def _print_event(event: str, data: dict) -> None:
    if event == "goal":
        print(f"> {data.get('goal', '')}\n")
    elif event == "tool_call":
        tool = data.get("tool", "?")
        args = data.get("arguments", {})
        args_str = args.get("command", "") if isinstance(args, dict) else str(args)
        if not args_str and isinstance(args, dict):
            args_str = ", ".join(f"{k}={v}" for k, v in args.items())
        print(f"[{tool}] {args_str}")
    elif event == "tool_result":
        result = str(data.get("result", ""))
        print(f"  -> {result[:100]}{'...' if len(result) > 100 else ''}")
    elif event == "final_answer":
        print(data.get("content", ""))
    elif event == "error":
        print(f"Erro: {data.get('error', '')}")
    elif event == "cancelled":
        print("Interrompido")
    elif event == "max_steps_reached":
        print("Limite de passos atingido")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lbot-harness")
    parser.add_argument("--show-thinking", action="store_true", default=True)
    parser.add_argument("--quiet", action="store_true", default=False)
    return parser


def main():
    args = _build_parser().parse_args()
    asyncio.run(_async_main(not args.quiet and args.show_thinking))


async def _async_main(show_thinking: bool):
    try:
        async with MCPClient() as client:
            await _run_repl(client, show_thinking)
    except ConnectionError as e:
        print(f"Erro: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAté logo!")


async def _run_repl(client: MCPClient, show_thinking: bool):
    agent = ReActAgent(client, on_event=_print_event if show_thinking else None)
    loop = asyncio.get_running_loop()
    running_task = None

    def _sigint_handler():
        if running_task and not running_task.done():
            agent.cancel()
        else:
            print("\nUse /exit para sair.")
            print("> ", end="", flush=True)

    try:
        loop.add_signal_handler(signal.SIGINT, _sigint_handler)
    except NotImplementedError:
        pass

    while True:
        try:
            user_input = await _get_input()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo!")
            break

        user_input = user_input.strip()
        if not user_input:
            continue
        if user_input.lower() in ("/exit", "/quit", "/q"):
            print("Até logo!")
            break

        try:
            running_task = asyncio.create_task(agent.run(user_input))
            result = await running_task
            if not show_thinking:
                print(result)
        except asyncio.CancelledError:
            print("Interrompido")
        except Exception as e:
            print(f"Erro: {e}")
        finally:
            running_task = None


async def _get_input() -> str:
    return await asyncio.get_running_loop().run_in_executor(None, lambda: input("> "))
