import pytest
import json
import respx
from httpx import Response
from src.adapters.ai.ollama_adapter import OllamaAdapter
from src.core.domain.entities import Message, MessageRole, ToolDefinition, ToolCall

@pytest.mark.asyncio
@respx.mock
async def test_stream_completion_success():
    adapter = OllamaAdapter()
    url = f"{adapter.base_url}/api/chat"
    
    # Simular respuesta de streaming de Ollama
    stream_content = [
        json.dumps({"message": {"role": "assistant", "content": "Hello"}, "done": False}) + "\n",
        json.dumps({"message": {"role": "assistant", "content": " world"}, "done": True}) + "\n"
    ]
    
    respx.post(url).mock(return_value=Response(200, content="".join(stream_content)))
    
    messages = [Message(role=MessageRole.USER, content="Hi")]
    chunks = []
    async for chunk in adapter.stream_completion(messages, []):
        chunks.append(chunk)
        
    assert len(chunks) == 2
    assert chunks[0].text == "Hello"
    assert chunks[1].text == " world"

@pytest.mark.asyncio
@respx.mock
async def test_stream_completion_tool_call():
    adapter = OllamaAdapter()
    url = f"{adapter.base_url}/api/chat"
    
    tool_data = json.dumps({
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"function": {"name": "get_stock", "arguments": {"id": 1}}}]
        },
        "done": True
    }) + "\n"
    
    respx.post(url).mock(return_value=Response(200, content=tool_data))
    
    chunks = []
    async for chunk in adapter.stream_completion([], []):
        chunks.append(chunk)
        
    assert len(chunks) == 1
    assert chunks[0].tool_calls[0].tool_name == "get_stock"
    assert chunks[0].tool_calls[0].arguments["id"] == 1

def test_map_tool_to_ollama():
    adapter = OllamaAdapter()
    tool = ToolDefinition(
        name="test", description="d", 
        input_schema={"type": "object"}, server_name="s"
    )
    mapped = adapter._map_tool_to_ollama(tool)
    assert mapped["type"] == "function"
    assert mapped["function"]["name"] == "test"

def test_map_messages_to_ollama():
    adapter = OllamaAdapter()
    messages = [
        Message(role=MessageRole.USER, content="A"),
        Message(role=MessageRole.ASSISTANT, content="B", tool_calls=[
            ToolCall(call_id="1", tool_name="t", arguments={})
        ])
    ]
    mapped = adapter._map_messages_to_ollama(messages)
    assert mapped[0]["role"] == "user"
    assert "tool_calls" in mapped[1]
