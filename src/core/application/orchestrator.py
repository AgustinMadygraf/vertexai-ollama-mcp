"""
Path: src/core/application/orchestrator.py
"""
import asyncio
import time
from typing import List, Optional
from src.core.domain.entities import Message, MessageRole, ToolCall, ToolResult, ToolDefinition, Intent, ChatSession
from src.core.domain.ports import AIEnginePort, MCPClientPort, ChatSessionRepositoryPort
from src.adapters.settings.logger import logger

class Orchestrator:
    def __init__(
        self, 
        ai_engine: AIEnginePort, 
        mcp_client: MCPClientPort,
        session_repo: ChatSessionRepositoryPort
    ):
        self.ai_engine = ai_engine
        self.mcp_client = mcp_client
        self.session_repo = session_repo

    async def process_message(self, user_prompt: str, session_id: str = "default") -> str:
        """
        Ciclo de vida de un mensaje con lógica de intención y persistencia.
        """
        logger.info(f"[{session_id}] Procesando prompt: '{user_prompt}'")
        start_time = time.time()
        
        # 1. Recuperar sesión (Memoria)
        session = await self.session_repo.get_session(session_id)
        session.add_message(Message(role=MessageRole.USER, content=user_prompt))

        # 2. Detección rápida de saludos
        greetings = ["hola", "buenos dias", "buenas tardes", "buen dia", "quien sos", "que haces"]
        if any(g in user_prompt.lower() for g in greetings):
            reply = (
                "👋 ¡Hola! Soy el Bridge MCP. Mi función es clasificar tus peticiones y "
                "ejecutar herramientas específicas en servidores conectados. ¿En qué puedo ayudarte?"
            )
            session.add_message(Message(role=MessageRole.ASSISTANT, content=reply))
            await self.session_repo.save_session(session)
            return reply

        try:
            # 3. Catálogo de herramientas
            tools = await self.mcp_client.list_tools()
            if not tools:
                return "No hay herramientas configuradas en los servidores MCP."
            
            # 4. Clasificación de intención
            intent: Optional[Intent] = await self.ai_engine.classify_intent(user_prompt, tools)
            
            if not intent:
                return "Lo siento, no pude procesar tu solicitud."

            # 5. Lógica de Confianza
            if intent.confidence < 0.35:
                logger.warning(f"[{session_id}] Baja confianza ({intent.confidence:.2f}) para: {intent.tool_name}")
                reply = "🤔 No estoy seguro de qué necesitas. ¿Podrías ser más específico?"
                session.add_message(Message(role=MessageRole.ASSISTANT, content=reply))
                await self.session_repo.save_session(session)
                return reply
            
            # 6. Ejecución de Herramienta
            tool_def = next((t for t in tools if t.name == intent.tool_name), None)
            arguments = await self.ai_engine.extract_arguments(user_prompt, tool_def) if tool_def else {}
            
            result: ToolResult = await self.mcp_client.call_tool(intent.tool_name, arguments)
            
            # 7. Persistir estado final
            session.add_message(Message(
                role=MessageRole.ASSISTANT, 
                content=f"Ejecutando {intent.tool_name}", 
                tool_calls=[ToolCall(call_id=result.call_id, tool_name=intent.tool_name, arguments=arguments)]
            ))
            session.add_message(Message(
                role=MessageRole.TOOL, 
                content=result.content, 
                tool_call_id=result.call_id
            ))
            
            await self.session_repo.save_session(session)

            if result.is_error:
                return f"❌ Error en {intent.tool_name}: {result.content}"
            
            return result.content

        except Exception as e:
            logger.error(f"Error crítico: {str(e)}", exc_info=True)
            return "Hubo un error interno. Por favor, reintenta."
