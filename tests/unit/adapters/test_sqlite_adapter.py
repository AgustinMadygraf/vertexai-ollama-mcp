import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from src.adapters.persistence.sqlite_adapter import SQLiteChatRepository
from src.core.domain.entities import ChatSession, Message, MessageRole, ToolCall

@pytest.mark.asyncio
async def test_sqlite_save_session_mock():
    # Mockear aiosqlite.connect
    with patch("aiosqlite.connect", new_callable=AsyncMock) as mock_connect:
        mock_db = mock_connect.return_value.__aenter__.return_value
        
        repo = SQLiteChatRepository(db_path="data/test.db")
        
        session = ChatSession(id="s1", messages=[
            Message(role=MessageRole.USER, content="Hello"),
            Message(role=MessageRole.ASSISTANT, content="Hi", tool_calls=[
                ToolCall(call_id="c1", tool_name="t1", arguments={"a": 1})
            ])
        ])
        
        await repo.save_session(session)
        
        # Verificar que se llamó a DELETE e INSERT
        assert mock_db.execute.call_count >= 3
        # Verificar que el segundo insert tiene el JSON de tool_calls
        call_args = mock_db.execute.call_args_list[2]
        query, params = call_args[0]
        assert "INSERT INTO messages" in query
        assert "t1" in params[3] # El JSON del tool_call

@pytest.mark.asyncio
async def test_sqlite_get_session_mock():
    with patch("aiosqlite.connect", new_callable=AsyncMock) as mock_connect:
        mock_db = mock_connect.return_value.__aenter__.return_value
        
        # Simular filas de la DB
        rows = [
            {"role": "user", "content": "Hello", "tool_calls": None, "tool_call_id": None},
            {"role": "assistant", "content": "Hi", "tool_calls": json.dumps([{"call_id": "1", "tool_name": "t1", "arguments": {}}]), "tool_call_id": None}
        ]
        
        # El cursor debe ser un gestor de contexto asíncrono
        mock_cursor = MagicMock()
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock(return_value=None)
        mock_cursor.fetchall = AsyncMock(return_value=rows)
        
        # execute() NO debe ser async, debe devolver el cursor
        mock_db.execute = MagicMock(return_value=mock_cursor)
        
        repo = SQLiteChatRepository(db_path="data/test.db")
        session = await repo.get_session("s1")
        
        assert len(session.messages) == 2
        assert session.messages[0].role == MessageRole.USER
        assert session.messages[1].tool_calls[0].tool_name == "t1"
