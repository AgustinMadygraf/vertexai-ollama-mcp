"""
Path: src/adapters/ai/vertex_adapter.py
"""
from typing import List, AsyncIterator, Dict, Any, Optional
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    Tool,
    FunctionDeclaration,
    Content,
    Part,
    GenerationConfig
)

from src.core.domain.ports import AIEnginePort
from src.core.domain.entities import (
    Message, MessageRole, ToolDefinition, 
    ToolCall, CompletionChunk, Intent
)
from src.adapters.settings.config import settings
from src.adapters.settings.logger import logger

class VertexAIAdapter(AIEnginePort):
    def __init__(self):
        # Inicializamos Vertex AI con las credenciales del entorno
        try:
            vertexai.init(
                project=settings.google_cloud_project,
                location=settings.google_cloud_location
            )
            self.model_name = settings.vertex_ai_model_name
            # El modelo se instancia con las herramientas en cada llamada si es necesario
            # pero guardamos una referencia base.
            self.base_model = GenerativeModel(self.model_name)
            logger.info(f"VertexAIAdapter inicializado con modelo: {self.model_name}")
        except Exception as e:
            logger.error(f"Error al inicializar Vertex AI: {e}")
            raise

    def _map_tool_to_vertex(self, tool: ToolDefinition) -> FunctionDeclaration:
        """
        Mapea una ToolDefinition de MCP a una FunctionDeclaration de Vertex AI.
        """
        # El formato parameters de Vertex AI es compatible con JSON Schema.
        # MCP ya provee un input_schema que sigue este estándar.
        schema = tool.input_schema
        
        # Aseguramos que el esquema tenga los campos mínimos requeridos por Vertex
        if "type" not in schema:
            schema["type"] = "object"
        
        return FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=schema
        )

    def _map_messages_to_vertex(self, messages: List[Message]) -> List[Content]:
        """
        Mapea los mensajes del dominio a objetos Content de Vertex AI,
        soportando el ciclo completo de Tool Calling.
        """
        vertex_messages = []
        for msg in messages:
            # Los mensajes de sistema se manejan por separado en system_instruction
            if msg.role == MessageRole.SYSTEM:
                continue 

            parts = []
            
            # 1. Manejar contenido de texto si existe
            if msg.content and msg.role != MessageRole.TOOL:
                parts.append(Part.from_text(msg.content))
            
            # 2. Determinar rol y mapear partes específicas de herramientas
            if msg.role == MessageRole.ASSISTANT:
                role = "model"
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        parts.append(Part.from_function_call(
                            name=tc.tool_name,
                            args=tc.arguments
                        ))
            
            elif msg.role == MessageRole.TOOL:
                role = "user" # Las respuestas de función en Vertex se envían como rol 'user'
                # Asumimos que content contiene el resultado serializado o el ID de la herramienta
                # En un sistema más complejo, el objeto ToolResult vendría aquí.
                parts.append(Part.from_function_response(
                    name=msg.tool_call_id or "unknown_tool",
                    response={"content": msg.content}
                ))
            
            else:
                role = "user"

            vertex_messages.append(Content(role=role, parts=parts))
        
        return vertex_messages

    async def stream_completion(
        self, 
        messages: List[Message], 
        tools: List[ToolDefinition]
    ) -> AsyncIterator[CompletionChunk]:
        """
        Envía el contexto a Gemini y emite fragmentos de respuesta o llamadas a herramientas.
        """
        # 1. Preparar herramientas si existen
        vertex_tools = None
        if tools:
            declarations = [self._map_tool_to_vertex(t) for t in tools]
            vertex_tools = [Tool(function_declarations=declarations)]

        # 2. Configurar modelo con instrucciones de sistema si el primer mensaje lo es
        system_instruction = None
        if messages and messages[0].role == MessageRole.SYSTEM:
            system_instruction = messages[0].content

        model = GenerativeModel(
            self.model_name,
            tools=vertex_tools,
            system_instruction=system_instruction
        )

        # 3. Mapear historial y último mensaje
        # Filtramos el mensaje de sistema para el historial de chat
        chat_messages = [m for m in messages if m.role != MessageRole.SYSTEM]
        
        if not chat_messages:
            yield CompletionChunk(text="Error: No hay mensajes de usuario para procesar.", is_final=True)
            return

        history = self._map_messages_to_vertex(chat_messages[:-1])
        last_message = chat_messages[-1].content

        # Iniciamos sesión de chat
        chat = model.start_chat(history=history)
        
        try:
            # Enviamos el mensaje de forma asíncrona y recibimos el stream
            response_stream = await chat.send_message_async(
                last_message, 
                stream=True
            )

            async for response in response_stream:
                chunk = CompletionChunk()
                
                # 1. Extraer texto si existe
                try:
                    if response.text:
                        chunk.text = response.text
                except ValueError:
                    # A veces response.text falla si el primer chunk es una FunctionCall
                    pass
                
                # 2. Extraer llamadas a herramientas
                if response.candidates[0].content.parts:
                    tool_calls = []
                    for part in response.candidates[0].content.parts:
                        if part.function_call:
                            fc = part.function_call
                            tool_calls.append(
                                ToolCall(
                                    call_id=f"call_{fc.name}", # ID sintético
                                    tool_name=fc.name,
                                    arguments=dict(fc.args)
                                )
                            )
                    if tool_calls:
                        chunk.tool_calls = tool_calls
                
                yield chunk

        except Exception as e:
            logger.error(f"Error en stream_completion de Vertex AI: {e}")
            yield CompletionChunk(text=f"Error en Vertex AI Engine: {str(e)}", is_final=True)

    async def classify_intent(
        self,
        prompt: str,
        tools: List[ToolDefinition]
    ) -> Optional[Intent]:
        """
        Usa Gemini para clasificar la intención rápidamente.
        """
        # Implementación opcional para cuando se prefiere bypassear el chat completo
        return None 

    async def extract_arguments(
        self,
        prompt: str,
        tool: ToolDefinition
    ) -> dict:
        """
        En Vertex AI, la extracción es automática vía tool calling. 
        Este método se deja por compatibilidad con el puerto.
        """
        return {}
