"""
Path: src/core/domain/ports.py
"""
from abc import ABC, abstractmethod
from typing import List, AsyncIterator, Optional
from src.core.domain.entities import Message, ToolDefinition, ToolCall, ToolResult, CompletionChunk, Intent

class AIEnginePort(ABC):
    @abstractmethod
    async def stream_completion(
        self, 
        messages: List[Message], 
        tools: List[ToolDefinition]
    ) -> AsyncIterator[CompletionChunk]:
        """Envía el historial y las herramientas disponibles a la IA y recibe un flujo de respuesta."""
        pass

    @abstractmethod
    async def classify_intent(
        self,
        prompt: str,
        tools: List[ToolDefinition]
    ) -> Optional[Intent]:
        """Versión de alta velocidad que mapea directamente un prompt a una herramienta sin chat."""
        pass

    @abstractmethod
    async def extract_arguments(
        self,
        prompt: str,
        tool: ToolDefinition
    ) -> dict:
        """Extrae los argumentos necesarios para una herramienta a partir del prompt."""
        pass

class MCPClientPort(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        """Inicializa la conexión con los servidores MCP."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Cierra todas las conexiones con los servidores MCP."""
        pass

    @abstractmethod
    async def list_tools(self) -> List[ToolDefinition]:
        """Obtiene el catálogo unificado de todas las herramientas de todos los servidores."""
        pass

    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: dict) -> ToolResult:
        """Ejecuta una herramienta específica en el servidor correspondiente."""
        pass

class ChatwootOutputPort(ABC):
    @abstractmethod
    async def send_message(self, account_id: int, conversation_id: int, content: str) -> bool:
        """Envía un mensaje de respuesta a una conversación específica en Chatwoot."""
        pass

class InfrastructureMonitorPort(ABC):
    @abstractmethod
    async def check_tunnel_status(self) -> dict:
        """Verifica el estado de salud del túnel en la API de Cloudflare."""
        pass

    @abstractmethod
    def validate_request_headers(self, headers: dict) -> bool:
        """Valida si los headers de una petición entrante son consistentes con Cloudflare."""
        pass
