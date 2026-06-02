import logging
import os
import sys
from typing import Any

from fastmcp import Client
from fastmcp.client.transports.stdio import StdioTransport

logger = logging.getLogger(__name__)

SERVER_COMMAND = [sys.executable, "-m", "mcp_server.server"]


class ConnectionError(Exception):
    pass


class MCPClient:
    def __init__(self, server_command: list[str] | None = None):
        self.server_command = server_command or SERVER_COMMAND
        self._client: Client | None = None

    def _build_transport(self) -> StdioTransport:
        cmd = self.server_command[0]
        args = self.server_command[1:]
        env = dict(os.environ)

        lbot_mcp_root = os.environ.get(
            "LBOT_MCP_ROOT",
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        )
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = lbot_mcp_root + "/src" + ":" + env["PYTHONPATH"]
        else:
            env["PYTHONPATH"] = lbot_mcp_root + "/src"

        return StdioTransport(command=cmd, args=args, env=env)

    async def __aenter__(self) -> "MCPClient":
        transport = self._build_transport()
        logger.info("Iniciando MCP Server: %s %s", transport.command, transport.args)

        try:
            self._client = Client(transport)
            await self._client.__aenter__()
        except Exception as e:
            raise ConnectionError(
                "não consigo me comunicar com meu corpo no momento"
            ) from e

        logger.info("MCP Server conectado e inicializado")
        return self

    async def __aexit__(self, *args):
        if self._client is not None:
            try:
                await self._client.__aexit__(None, None, None)
            except Exception:
                pass
            self._client = None
        logger.info("MCP Client encerrado")

    async def list_tools(self) -> list[dict[str, Any]]:
        if self._client is None:
            raise ConnectionError("Cliente não conectado.")

        result = await self._client.list_tools_mcp()
        tools = []
        for tool in result.tools:
            tools.append({
                "name": tool.name,
                "description": tool.description or "",
                "inputSchema": tool.inputSchema,
            })
        return tools

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> str:
        if self._client is None:
            raise ConnectionError("Cliente não conectado.")

        result = await self._client.call_tool_mcp(name, arguments or {})

        if result.isError:
            error_text = ""
            for content in result.content:
                if hasattr(content, "text"):
                    error_text += content.text
            raise RuntimeError(error_text or f"Erro na ferramenta '{name}'")

        texts = []
        for content in result.content:
            if hasattr(content, "text"):
                texts.append(content.text)

        return "\n".join(texts) if texts else str(result.content)
