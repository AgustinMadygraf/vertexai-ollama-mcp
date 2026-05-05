from src.core.domain.entities import Message, ToolDefinition, ToolCall, MessageRole

def test_message_creation():
    msg = Message(role=MessageRole.USER, content="Hola")
    assert msg.role == MessageRole.USER
    assert msg.content == "Hola"
    assert msg.tool_calls is None

def test_tool_definition():
    tool = ToolDefinition(name="test", description="desc", input_schema={}, server_name="srv")
    assert tool.name == "test"
    assert tool.server_name == "srv"

def test_tool_call_serialization():
    call = ToolCall(call_id="123", tool_name="calc", arguments={"a": 1})
    assert call.call_id == "123"
    assert call.tool_name == "calc"
    assert call.arguments["a"] == 1
