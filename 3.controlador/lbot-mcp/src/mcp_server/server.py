import logging
import os
import sys
from contextlib import asynccontextmanager

from fastmcp import FastMCP

from .backends.base import LBotBackend

if __name__ == "__main__":
    sys.modules["mcp_server.server"] = sys.modules["__main__"]
    setattr(sys.modules["mcp_server"], "server", sys.modules["__main__"])

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_server):
    import mcp_server.context as ctx

    from .services.inference import close_inference

    try:
        yield
    finally:
        if ctx._control and ctx._control._task and not ctx._control._task.done():
            await ctx._control.stop()
        if ctx.backend:
            await ctx.backend.close()
        await close_inference()


mcp = FastMCP("LBot", lifespan=lifespan)


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

    import mcp_server.tools.approach  # noqa: F401
    import mcp_server.tools.camera  # noqa: F401
    import mcp_server.tools.movement  # noqa: F401
    import mcp_server.tools.proximity  # noqa: F401
    import mcp_server.tools.search_object  # noqa: F401
    import mcp_server.tools.stop  # noqa: F401

    logger.info(
        "Tools registradas: camera, proximity, move, search_object, approach, stop"
    )
    mcp.run(show_banner=False)


if __name__ == "__main__":
    main()
