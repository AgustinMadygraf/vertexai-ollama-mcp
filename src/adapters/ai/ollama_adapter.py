"""
Path: src/adapters/ai/ollama_adapter.py
"""
import json
import httpx
from typing import List, AsyncIterator, Optional, Dict, Any

from src.core.domain.ports import AIEnginePort
from src.core.domain.entities import (
    Message, MessageRole, ToolDefinition, 
    ToolCall, CompletionChunk, Intent
)
from src.adapters.settings.config import settings
from src.adapters.settings.logger import logger

class OllamaAdapter(AIEnginePort):
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model_name = settings.ollama_model
        self.timeout = httpx.Timeout(60.0, connect=10.0)
        logger.info(f"OllamaAdapter inicializado: {self.base_url} (Modelo: {self.model_name})")

    def _map_tool_to_ollama(self, tool: ToolDefinition) -> Dict[str, Any]:
        """Convierte una herramienta al formato de Ollama."""
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema
            }
        }

    def _map_messages_to_ollama(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Mapea historial al formato de mensajes de Ollama."""
        ollama_msgs = []
        for msg in messages:
            role = msg.role.value
            if msg.role == MessageRole.ASSISTANT:
                role = "assistant"
            
            content = msg.content
            tool_calls = None
            
            if msg.tool_calls:
                tool_calls = [
                    {
                        "function": {
                            "name": tc.tool_name,
                            "arguments": tc.arguments
                        }
                    } for tc in msg.tool_calls
                ]

            m = {"role": role, "content": content}
            if tool_calls:
                m["tool_calls"] = tool_calls
            
            # En Ollama, las respuestas de herramientas usan role: 'tool'
            if msg.role == MessageRole.TOOL:
                # El campo 'tool_call_id' no es estrictamente obligatorio en Ollama 
                # pero ayuda a la coherencia.
                pass

            ollama_msgs.append(m)
        return ollama_msgs

    async def stream_completion(
        self, 
        messages: List[Message], 
        tools: List[ToolDefinition]
    ) -> AsyncIterator[CompletionChunk]:
        """Envía el prompt a Ollama y procesa el stream de respuesta."""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model_name,
            "messages": self._map_messages_to_ollama(messages),
            "stream": True
        }
        
        if tools:
            payload["tools"] = [self._map_tool_to_ollama(t) for t in tools]

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(f"Error de Ollama ({response.status_code}): {error_text.decode()}")
                        yield CompletionChunk(text=f"Error en Ollama: {response.status_code}", is_final=True)
                        return

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        
                        data = json.loads(line)
                        chunk = CompletionChunk()
                        
                        # Manejar mensaje de texto
                        message_data = data.get("message", {})
                        if "content" in message_data:
                            chunk.text = message_data["content"]
                        
                        # Manejar llamadas a herramientas
                        if "tool_calls" in message_data:
                            tool_calls = []
                            for tc in message_data["tool_calls"]:
                                func = tc.get("function", {})
                                tool_calls.append(
                                    ToolCall(
                                        call_id="call_" + func.get("name", "unknown"),
                                        tool_name=func.get("name"),
                                        arguments=func.get("arguments", {})
                                    )
                                )
                            chunk.tool_calls = tool_calls
                        
                        if data.get("done"):
                            chunk.is_final = True
                        
                        yield chunk

        except Exception as e:
            logger.error(f"Fallo de conexión con Ollama: {e}")
            yield CompletionChunk(text=f"Error: No se pudo conectar con Ollama en {self.base_url}", is_final=True)

    async def classify_intent(self, prompt: str, tools: List[ToolDefinition]) -> Optional[Intent]:
        # Implementación delegada al motor de clasificación rápida si es necesario
        return None

    async def extract_arguments(self, prompt: str, tool: ToolDefinition) -> dict:
        return {}
