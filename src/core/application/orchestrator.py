"""
Path: src/core/application/orchestrator.py
"""
import asyncio
from typing import List, Optional
from src.core.domain.entities import Message, MessageRole, ToolCall, ToolResult, ToolDefinition
from src.core.domain.ports import AIEnginePort, MCPClientPort
from src.adapters.settings.logger import logger

class Orchestrator:
    def __init__(self, ai_engine: AIEnginePort, mcp_client: MCPClientPort):
        self.ai_engine = ai_engine
        self.mcp_client = mcp_client

    async def process_message(self, user_prompt: str) -> str:
        """
        Ciclo de vida de un mensaje:
        1. Obtiene herramientas de los servidores MCP.
        2. Clasifica la intención del usuario usando el motor de IA.
        3. Si hay una herramienta, la ejecuta y devuelve el resultado.
        """
        logger.info(f"Procesando prompt: '{user_prompt}'")
        
        try:
            # 1. Catálogo de herramientas
            tools = await self.mcp_client.list_tools()
            
            # 2. Clasificación de intención (Vía rápida)
            tool_call = await self.ai_engine.classify_intent(user_prompt, tools)
            
            if not tool_call:
                return "No estoy seguro de qué herramienta usar para esa solicitud. ¿Podrías ser más específico?"
            
            # 3. Ejecución de la herramienta
            logger.info(f"Ejecutando herramienta: {tool_call.tool_name}")
            result: ToolResult = await self.mcp_client.call_tool(
                tool_call.tool_name, 
                tool_call.arguments
            )
            
            if result.is_error:
                return f"❌ Error al ejecutar {tool_call.tool_name}: {result.content}"
            
            return result.content

        except Exception as e:
            logger.error(f"Error crítico en el orquestador: {str(e)}")
            return f"Hubo un error interno al procesar tu solicitud: {str(e)}"
