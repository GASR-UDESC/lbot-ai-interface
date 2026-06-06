import os
import logging
import sys

from fastmcp import FastMCP

from .backends.base import LBotBackend

if __name__ == "__main__":
    sys.modules["mcp_server.server"] = sys.modules["__main__"]
    sys.modules["mcp_server"].server = sys.modules["__main__"]

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stderr,
)
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

    backend = create_backend(backend_name)

    import mcp_server.context as ctx

    ctx.backend = backend

    import mcp_server.tools.camera  # noqa: F401
    import mcp_server.tools.proximity  # noqa: F401
    import mcp_server.tools.movement  # noqa: F401
    import mcp_server.tools.translate  # noqa: F401

    logger.info("Tools registradas: camera, proximity, move, translate")
    mcp.run(show_banner=False)


if __name__ == "__main__":
    main()
