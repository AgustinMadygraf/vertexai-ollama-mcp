"""
Path: src/adapters/mcp/process_manager.py
"""

from contextlib import AsyncExitStack
from typing import Dict, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.core.domain.ports import MCPClientPort
from src.core.domain.entities import ToolDefinition, ToolResult
from src.adapters.settings.config import load_mcp_config, McpServerConfig
from src.adapters.settings.logger import logger

class MultiProcessManager(MCPClientPort):
    def __init__(self):
        self.configs: Dict[str, McpServerConfig] = load_mcp_config()
        self.sessions: Dict[str, ClientSession] = {}
        self._exit_stack = AsyncExitStack()
        self._tool_to_server: Dict[str, str] = {}

    async def initialize(self) -> None:
        """Inicia todos los servidores MCP configurados usando AsyncExitStack para mantener los contextos vivos."""
        for name, cfg in self.configs.items():
            try:
                logger.info(f"Iniciando servidor MCP: {name}...")
                server_params = StdioServerParameters(
                    command=cfg.command,
                    args=cfg.args,
                    env=cfg.env
                )
                
                # Iniciamos el transporte stdio y lo añadimos al stack para que no se cierre
                read_stream, write_stream = await self._exit_stack.enter_async_context(stdio_client(server_params))
                
                # Iniciamos la sesión y la añadimos al stack
                session = await self._exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
                
                # Inicialización protocolar
                await session.initialize()
                
                self.sessions[name] = session
                logger.info(f"Servidor {name} inicializado con éxito.")
                
            except Exception as e:
                logger.error(f"Error al iniciar servidor {name}: {str(e)}")

    async def list_tools(self) -> List[ToolDefinition]:
        """Obtiene y mapea todas las herramientas de todos los servidores activos."""
        all_tools = []
        self._tool_to_server = {} # Limpiamos el mapeo previo
        
        for server_name, session in self.sessions.items():
            try:
                response = await session.list_tools()
                for tool in response.tools:
                    # Guardamos el mapeo para saber a quién llamar luego
                    self._tool_to_server[tool.name] = server_name
                    
                    all_tools.append(ToolDefinition(
                        name=tool.name,
                        description=tool.description or "",
                        input_schema=tool.inputSchema,
                        server_name=server_name
                    ))
            except Exception as e:
                logger.error(f"Error listando herramientas de {server_name}: {str(e)}")
        
        return all_tools

    async def call_tool(self, tool_name: str, arguments: dict) -> ToolResult:
        """Enruta la llamada al servidor correspondiente."""
        server_name = self._tool_to_server.get(tool_name)
        if not server_name:
            return ToolResult(call_id="", content=f"Error: Herramienta '{tool_name}' no encontrada.", is_error=True)
        
        session = self.sessions.get(server_name)
        try:
            logger.debug(f"Llamando a {tool_name} en servidor {server_name}...")
            result = await session.call_tool(tool_name, arguments)
            
            # El SDK de MCP devuelve un objeto con 'content' que es una lista
            # Combinamos el contenido para nuestro dominio
            text_content = "\n".join([c.text for c in result.content if hasattr(c, 'text')])
            
            return ToolResult(
                call_id="", # El ID se gestiona a nivel de sesión si es necesario
                content=text_content
            )
        except Exception as e:
            logger.error(f"Error ejecutando {tool_name}: {str(e)}")
            return ToolResult(call_id="", content=str(e), is_error=True)

    async def stop(self) -> None:
        """Cierra todas las sesiones activas y sus transportes."""
        logger.info("Cerrando todos los servidores MCP...")
        await self._exit_stack.aclose()
        self.sessions.clear()
