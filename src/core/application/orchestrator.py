"""
Path: src/core/application/orchestrator.py
"""
import asyncio
import time
from typing import List, Optional
from src.core.domain.entities import Message, MessageRole, ToolCall, ToolResult, ToolDefinition, Intent
from src.core.domain.ports import AIEnginePort, MCPClientPort
from src.adapters.settings.logger import logger

class Orchestrator:
    def __init__(self, ai_engine: AIEnginePort, mcp_client: MCPClientPort):
        self.ai_engine = ai_engine
        self.mcp_client = mcp_client

    async def process_message(self, user_prompt: str) -> str:
        """
        Ciclo de vida de un mensaje con observabilidad y ruteo semántico.
        """
        logger.info(f"Procesando prompt: '{user_prompt}'")
        start_time = time.time()
        
        try:
            # 1. Catálogo de herramientas
            tools = await self.mcp_client.list_tools()
            
            # 2. Clasificación de intención (Local GPU)
            intent: Optional[Intent] = await self.ai_engine.classify_intent(user_prompt, tools)
            
            if not intent:
                return "No se encontraron herramientas disponibles en los servidores MCP."
            
            logger.info(f"Ejecución forzada: {intent.tool_name} (Confianza: {intent.confidence:.2f})")
            
            logger.info(f"Intento clasificado: {intent.tool_name} (Confianza: {intent.confidence:.2f})")

            # 3. Ejecución de la herramienta
            result: ToolResult = await self.mcp_client.call_tool(
                intent.tool_name, 
                {} # TODO: Extractor de argumentos
            )
            
            elapsed = time.time() - start_time
            logger.info(f"Proceso completado en {elapsed:.2f}s")

            if result.is_error:
                return f"❌ Error en {intent.tool_name}: {result.content}"
            
            return result.content

        except Exception as e:
            logger.error(f"Error crítico en el orquestador: {str(e)}", exc_info=True)
            return f"Hubo un error interno: {str(e)}"
