"""
Path: src/adapters/persistence/sqlite_adapter.py
"""
import json
import aiosqlite
import os
from typing import List, Optional
from src.core.domain.ports import ChatSessionRepositoryPort
from src.core.domain.entities import ChatSession, Message, MessageRole, ToolCall
from src.adapters.settings.logger import logger

class SQLiteChatRepository(ChatSessionRepositoryPort):
    def __init__(self, db_path: str = "data/chat_history.db"):
        self.db_path = db_path
        # Aseguramos que el directorio exista si se especifica una ruta de archivo
        dirname = os.path.dirname(self.db_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

    async def _get_connection(self):
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        return conn

    async def initialize(self):
        """Crea las tablas si no existen."""
        async with await self._get_connection() as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT,
                    tool_calls TEXT,
                    tool_call_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id)")
            await db.commit()
        logger.info(f"Base de datos SQLite inicializada en {self.db_path}")

    async def get_session(self, session_id: str) -> ChatSession:
        async with await self._get_connection() as db:
            async with db.execute(
                "SELECT role, content, tool_calls, tool_call_id FROM messages WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                
                messages = []
                for row in rows:
                    tool_calls = None
                    if row["tool_calls"]:
                        raw_calls = json.loads(row["tool_calls"])
                        tool_calls = [ToolCall(**tc) for tc in raw_calls]
                    
                    messages.append(Message(
                        role=MessageRole(row["role"]),
                        content=row["content"] or "",
                        tool_calls=tool_calls,
                        tool_call_id=row["tool_call_id"]
                    ))
                
                return ChatSession(id=session_id, messages=messages)

    async def save_session(self, session: ChatSession) -> None:
        """
        Guarda solo los mensajes que no están en la DB. 
        En una implementación real, podríamos usar un flag 'is_persisted'.
        Aquí, por simplicidad, vaciamos y volvemos a escribir el historial corto 
        o simplemente insertamos los nuevos. 
        Implementaremos 'borrar y reinsertar' para asegurar sincronía perfecta.
        """
        async with await self._get_connection() as db:
            # Primero limpiamos el historial anterior de esta sesión
            await db.execute("DELETE FROM messages WHERE session_id = ?", (session.id,))
            
            # Insertamos todo el historial actual
            for msg in session.messages:
                tool_calls_json = None
                if msg.tool_calls:
                    tool_calls_json = json.dumps([
                        {"call_id": tc.call_id, "tool_name": tc.tool_name, "arguments": tc.arguments}
                        for tc in msg.tool_calls
                    ])
                
                await db.execute(
                    "INSERT INTO messages (session_id, role, content, tool_calls, tool_call_id) VALUES (?, ?, ?, ?, ?)",
                    (session.id, msg.role.value, msg.content, tool_calls_json, msg.tool_call_id)
                )
            
            await db.commit()

    async def clear_session(self, session_id: str) -> None:
        async with await self._get_connection() as db:
            await db.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            await db.commit()
            logger.info(f"Historial de sesión {session_id} eliminado.")
