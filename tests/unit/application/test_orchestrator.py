import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.application.orchestrator import Orchestrator
from src.core.domain.entities import ToolCall, ToolResult, ToolDefinition, Intent

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.application.orchestrator import Orchestrator
from src.core.domain.entities import ToolCall, ToolResult, ToolDefinition, Intent

@pytest.mark.asyncio
async def test_orchestrator_greeting():
    # Test para la nueva lógica de saludos
    mock_ai = AsyncMock()
    mock_mcp = AsyncMock()
    
    orchestrator = Orchestrator(mock_ai, mock_mcp)
    response = await orchestrator.process_message("Hola")
    
    assert "¡Hola! Soy el Bridge MCP" in response
    mock_ai.classify_intent.assert_not_called()

@pytest.mark.asyncio
async def test_orchestrator_success():
    mock_ai = AsyncMock()
    mock_mcp = AsyncMock()
    
    # Setup behavior
    mock_mcp.list_tools.return_value = [
        ToolDefinition(name="get_stock", description="Check stock", input_schema={}, server_name="srv")
    ]
    mock_ai.classify_intent.return_value = Intent(
        tool_name="get_stock", confidence=0.9
    )
    mock_mcp.call_tool.return_value = ToolResult(call_id="1", content="Stock: 10")
    
    orchestrator = Orchestrator(mock_ai, mock_mcp)
    response = await orchestrator.process_message("¿Stock disponible?")
    
    assert "Stock: 10" in response
    mock_ai.classify_intent.assert_called_once()
    mock_mcp.call_tool.assert_called_once()

@pytest.mark.asyncio
async def test_orchestrator_no_intent():
    mock_ai = AsyncMock()
    mock_mcp = AsyncMock()
    mock_mcp.list_tools.return_value = [ToolDefinition(name="t1", description="d1", input_schema={}, server_name="s1")]
    mock_ai.classify_intent.return_value = None
    
    orchestrator = Orchestrator(mock_ai, mock_mcp)
    response = await orchestrator.process_message("peticion desconocida")
    
    assert "no pude procesar tu solicitud" in response
    mock_mcp.call_tool.assert_not_called()

@pytest.mark.asyncio
async def test_orchestrator_low_confidence():
    mock_ai = AsyncMock()
    mock_mcp = AsyncMock()
    mock_mcp.list_tools.return_value = [ToolDefinition(name="t1", description="d1", input_schema={}, server_name="s1")]
    mock_ai.classify_intent.return_value = Intent(tool_name="t1", confidence=0.1)
    
    orchestrator = Orchestrator(mock_ai, mock_mcp)
    response = await orchestrator.process_message("query")
    
    assert "No estoy muy seguro de qué herramienta necesitas" in response

@pytest.mark.asyncio
async def test_orchestrator_tool_error():
    mock_ai = AsyncMock()
    mock_mcp = AsyncMock()
    mock_mcp.list_tools.return_value = [ToolDefinition(name="err", description="d", input_schema={}, server_name="s")]
    mock_ai.classify_intent.return_value = Intent(tool_name="err", confidence=0.8)
    mock_mcp.call_tool.return_value = ToolResult(call_id="1", content="Fatal Error", is_error=True)
    
    orchestrator = Orchestrator(mock_ai, mock_mcp)
    response = await orchestrator.process_message("ejecutar error")
    
    assert "❌ Hubo un problema al ejecutar" in response
