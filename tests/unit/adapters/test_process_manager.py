import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.adapters.mcp.process_manager import MultiProcessManager
from src.adapters.settings.config import McpServerConfig

@pytest.fixture
def mock_mcp_sdk():
    with patch("src.adapters.mcp.process_manager.stdio_client") as mock_stdio, \
         patch("src.adapters.mcp.process_manager.ClientSession") as mock_session:
        
        # Setup stdio_client mock
        mock_stdio.return_value.__aenter__.return_value = (MagicMock(), MagicMock())
        
        # Setup ClientSession mock
        session_instance = mock_session.return_value.__aenter__.return_value
        session_instance.initialize = AsyncMock()
        session_instance.list_tools = AsyncMock()
        session_instance.call_tool = AsyncMock()
        
        yield {
            "stdio": mock_stdio,
            "session": mock_session,
            "session_instance": session_instance
        }

@pytest.mark.asyncio
async def test_process_manager_initialize(mock_mcp_sdk):
    # Simular configuración de 2 servidores
    configs = {
        "srv1": McpServerConfig(command="python", args=["m1.py"], env={}),
        "srv2": McpServerConfig(command="python", args=["m2.py"], env={})
    }
    
    with patch("src.adapters.mcp.process_manager.load_mcp_config", return_value=configs):
        manager = MultiProcessManager()
        await manager.initialize()
        
        assert len(manager.sessions) == 2
        assert mock_mcp_sdk["stdio"].call_count == 2
        assert mock_mcp_sdk["session_instance"].initialize.call_count == 2

@pytest.mark.asyncio
async def test_process_manager_list_tools(mock_mcp_sdk):
    configs = {"srv1": McpServerConfig(command="p", args=[], env={})}
    
    # Mock de respuesta de herramientas
    mock_tool = MagicMock()
    mock_tool.name = "my_tool"
    mock_tool.description = "desc"
    mock_tool.inputSchema = {"type": "object"}
    
    mock_response = MagicMock()
    mock_response.tools = [mock_tool]
    mock_mcp_sdk["session_instance"].list_tools.return_value = mock_response

    with patch("src.adapters.mcp.process_manager.load_mcp_config", return_value=configs):
        manager = MultiProcessManager()
        await manager.initialize()
        tools = await manager.list_tools()
        
        assert len(tools) == 1
        assert tools[0].name == "my_tool"
        assert manager._tool_to_server["my_tool"] == "srv1"

@pytest.mark.asyncio
async def test_process_manager_call_tool(mock_mcp_sdk):
    configs = {"srv1": McpServerConfig(command="p", args=[], env={})}
    
    # Setup list_tools to populate the mapping
    mock_tool = MagicMock()
    mock_tool.name = "action"
    mock_tool.inputSchema = {}
    mock_response = MagicMock()
    mock_response.tools = [mock_tool]
    mock_mcp_sdk["session_instance"].list_tools.return_value = mock_response

    # Setup call_tool response
    mock_content = MagicMock()
    mock_content.text = "Result from MCP"
    mock_call_result = MagicMock()
    mock_call_result.content = [mock_content]
    mock_mcp_sdk["session_instance"].call_tool.return_value = mock_call_result

    with patch("src.adapters.mcp.process_manager.load_mcp_config", return_value=configs):
        manager = MultiProcessManager()
        await manager.initialize()
        await manager.list_tools() # Para llenar _tool_to_server
        
        result = await manager.call_tool("action", {"param": 1})
        
        assert result.content == "Result from MCP"
        mock_mcp_sdk["session_instance"].call_tool.assert_called_once_with("action", {"param": 1})

@pytest.mark.asyncio
async def test_process_manager_stop(mock_mcp_sdk):
    manager = MultiProcessManager()
    with patch.object(manager._exit_stack, "aclose", new_callable=AsyncMock) as mock_aclose:
        await manager.stop()
        mock_aclose.assert_called_once()
        assert len(manager.sessions) == 0
