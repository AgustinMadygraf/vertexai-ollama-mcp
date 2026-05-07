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

    async def process_message(self, user_prompt: str, session_id: str = "default") -> str:
        """
        Ciclo de vida de un mensaje con lógica de intención (Opción D).
        """
        logger.info(f"[{session_id}] Procesando prompt: '{user_prompt}'")
        start_time = time.time()
        
        # 0. Detección rápida de saludos (Keywords + Semántica simple)
        greetings = ["hola", "buenos dias", "buenas tardes", "buen dia", "quien sos", "que haces"]
        if any(g in user_prompt.lower() for g in greetings):
            return (
                "👋 ¡Hola! Soy el Bridge MCP. Mi función es clasificar tus peticiones y "
                "ejecutar herramientas específicas en servidores conectados (WooCommerce, Xubio, etc.). "
                "¿En qué puedo ayudarte hoy?"
            )

        try:
            # 1. Catálogo de herramientas
            tools = await self.mcp_client.list_tools()
            if not tools:
                return "No hay herramientas configuradas en los servidores MCP."
            
            # 2. Clasificación de intención (Local GPU)
            intent: Optional[Intent] = await self.ai_engine.classify_intent(user_prompt, tools)
            
            if not intent:
                return "Lo siento, no pude procesar tu solicitud."

            # --- Lógica de Confianza (Opción D) ---
            # Umbral de duda: Si la confianza es menor a 0.35, pedimos aclaración
            if intent.confidence < 0.35:
                logger.warning(f"[{session_id}] Baja confianza detectada ({intent.confidence:.2f}) para: {intent.tool_name}")
                return (
                    "🤔 No estoy muy seguro de qué herramienta necesitas. "
                    "¿Podrías ser más específico? Por ejemplo: 'ver pedidos de WooCommerce' o 'listar clientes'."
                )
            
            # Umbral de "casi seguro": Si está entre 0.35 y 0.5, mencionamos la duda pero procedemos
            # (Esto es opcional, pero ayuda a la transparencia)
            
            logger.info(f"[{session_id}] Intento validado: {intent.tool_name} (Confianza: {intent.confidence:.2f})")

            # Buscar la definición de la herramienta para extraer argumentos
            tool_def = next((t for t in tools if t.name == intent.tool_name), None)
            
            # 3. Extracción de argumentos
            arguments = {}
            if tool_def:
                arguments = await self.ai_engine.extract_arguments(user_prompt, tool_def)
                logger.info(f"[{session_id}] Argumentos extraídos: {arguments}")

            # 4. Ejecución de la herramienta
            result: ToolResult = await self.mcp_client.call_tool(
                intent.tool_name, 
                arguments
            )
            
            elapsed = time.time() - start_time
            logger.info(f"[{session_id}] Proceso completado en {elapsed:.2f}s")

            if result.is_error:
                return f"❌ Hubo un problema al ejecutar {intent.tool_name}: {result.content}"
            
            return result.content

        except Exception as e:
            logger.error(f"Error crítico en el orquestador: {str(e)}", exc_info=True)
            return "Hubo un error interno procesando tu solicitud. Por favor, reintenta en un momento."
