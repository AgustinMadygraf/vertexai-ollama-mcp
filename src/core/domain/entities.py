"""
Path: src/core/domain/entities.py
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, AsyncIterator

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

@dataclass(frozen=True)
class Intent:
    tool_name: str
    confidence: float
    reason: str = ""

@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str  # Para saber a qué servidor pertenece

@dataclass(frozen=True)
class ToolCall:
    call_id: str
    tool_name: str
    arguments: Dict[str, Any]

@dataclass(frozen=True)
class ToolResult:
    call_id: str
    content: str
    is_error: bool = False

@dataclass
class Message:
    role: MessageRole
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None  # Para mensajes de rol TOOL

@dataclass
class CompletionChunk:
    text: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    is_final: bool = False

@dataclass
class ChatSession:
    id: str
    messages: List[Message] = field(default_factory=list)
    
    def add_message(self, message: Message):
        self.messages.append(message)
    
    def get_history(self) -> List[Message]:
        return self.messages
