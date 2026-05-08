import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.adapters.ai.vertex_adapter import VertexAIAdapter
from src.core.domain.entities import Message, MessageRole, ToolDefinition, ToolCall

@pytest.fixture
def mock_vertex():
    with patch("src.adapters.ai.vertex_adapter.vertexai.init") as mock_init, \
         patch("src.adapters.ai.vertex_adapter.GenerativeModel") as mock_model, \
         patch("src.adapters.ai.vertex_adapter.Part") as mock_part, \
         patch("src.adapters.ai.vertex_adapter.Content") as mock_content, \
         patch("src.adapters.ai.vertex_adapter.FunctionDeclaration") as mock_fd:
        yield {
            "init": mock_init,
            "model": mock_model,
            "part": mock_part,
            "content": mock_content,
            "fd": mock_fd
        }

def test_vertex_adapter_init(mock_vertex):
    adapter = VertexAIAdapter()
    mock_vertex["init"].assert_called_once()
    assert adapter.model_name is not None

def test_map_tool_to_vertex(mock_vertex):
    adapter = VertexAIAdapter()
    tool = ToolDefinition(
        name="test_tool",
        description="A test tool",
        input_schema={"type": "object", "properties": {"arg1": {"type": "string"}}},
        server_name="test_server"
    )
    
    adapter._map_tool_to_vertex(tool)
    mock_vertex["fd"].assert_called_once()
    args, kwargs = mock_vertex["fd"].call_args
    assert kwargs["name"] == "test_tool"

def test_map_messages_to_vertex(mock_vertex):
    adapter = VertexAIAdapter()
    messages = [
        Message(role=MessageRole.USER, content="Hello"),
        Message(role=MessageRole.ASSISTANT, content="Hi", tool_calls=[
            ToolCall(call_id="1", tool_name="tool1", arguments={"a": 1})
        ]),
        Message(role=MessageRole.TOOL, content="Result", tool_call_id="1")
    ]
    
    adapter._map_messages_to_vertex(messages)
    
    # Vertex: USER -> 'user', ASSISTANT -> 'model', TOOL -> 'user'
    assert mock_vertex["content"].call_count == 3
    mock_vertex["part"].from_function_response.assert_called_once()
    mock_vertex["part"].from_function_call.assert_called_once()

@pytest.mark.asyncio
async def test_stream_completion_basic(mock_vertex):
    mock_model_instance = mock_vertex["model"].return_value
    mock_chat = mock_model_instance.start_chat.return_value
    
    # Mock de la respuesta de Gemini
    mock_response = MagicMock()
    mock_response.text = "Hello from AI"
    mock_response.candidates = [MagicMock()]
    mock_response.candidates[0].content.parts = [MagicMock(text="Hello from AI", function_call=None)]
    
    # Corrutina que devuelve un iterador asíncrono
    async def mock_gen():
        yield mock_response

    mock_chat.send_message_async = AsyncMock(return_value=mock_gen())
    
    adapter = VertexAIAdapter()
    messages = [Message(role=MessageRole.USER, content="Hi")]
    
    chunks = []
    async for chunk in adapter.stream_completion(messages, []):
        chunks.append(chunk)
        
    assert len(chunks) > 0
    assert chunks[0].text == "Hello from AI"
