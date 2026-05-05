import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.application.orchestrator import Orchestrator
from src.core.domain.entities import ToolCall, ToolResult, ToolDefinition

@pytest.mark.asyncio
async def test_orchestrator_success():
    # Mocks
    mock_ai = AsyncMock()
    mock_mcp = AsyncMock()
    
    # Setup behavior
    mock_mcp.list_tools.return_value = [
        ToolDefinition(name="get_stock", description="Check stock", input_schema={}, server_name="srv")
    ]
    mock_ai.classify_intent.return_value = ToolCall(
        call_id="1", tool_name="get_stock", arguments={"product": "t-shirt"}
    )
    mock_mcp.call_tool.return_value = ToolResult(call_id="1", content="Stock: 10")
    
    orchestrator = Orchestrator(mock_ai, mock_mcp)
    response = await orchestrator.process_message("¿Cuanto stock hay?")
    
    assert response == "Stock: 10"
    mock_ai.classify_intent.assert_called_once()
    mock_mcp.call_tool.assert_called_once_with("get_stock", {"product": "t-shirt"})

@pytest.mark.asyncio
async def test_orchestrator_no_intent():
    mock_ai = AsyncMock()
    mock_mcp = AsyncMock()
    mock_ai.classify_intent.return_value = None
    
    orchestrator = Orchestrator(mock_ai, mock_mcp)
    response = await orchestrator.process_message("Hola")
    
    assert "No estoy seguro" in response
    mock_mcp.call_tool.assert_not_called()

@pytest.mark.asyncio
async def test_orchestrator_tool_error():
    mock_ai = AsyncMock()
    mock_mcp = AsyncMock()
    mock_ai.classify_intent.return_value = ToolCall(call_id="1", tool_name="err", arguments={})
    mock_mcp.call_tool.return_value = ToolResult(call_id="1", content="Fatal Error", is_error=True)
    
    orchestrator = Orchestrator(mock_ai, mock_mcp)
    response = await orchestrator.process_message("error")
    
    assert "❌ Error" in response
    assert "Fatal Error" in response
