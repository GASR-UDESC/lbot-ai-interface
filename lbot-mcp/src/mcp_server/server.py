import os
import logging

from fastmcp import FastMCP

from .backends.base import LBotBackend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("LBot")


def create_backend(name: str | None = None) -> LBotBackend:
    backend_name = name or os.environ.get("LBOT_BACKEND", "simulator")

    if backend_name == "simulator":
        from .backends.simulator import SimulatorBackend

        base_url = os.environ.get("LBOT_SIMULATOR_URL", "http://localhost:3001")
        return SimulatorBackend(base_url=base_url)

    raise ValueError(f"Backend desconhecido: '{backend_name}'. Use 'simulator'.")


def main():
    backend_name = os.environ.get("LBOT_BACKEND", "simulator")
    logger.info("Iniciando LBot MCP Server com backend '%s'", backend_name)
    mcp.run()


if __name__ == "__main__":
    main()
