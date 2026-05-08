import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from src.adapters.cli.app import interactive_loop

@pytest.mark.asyncio
async def test_interactive_loop_exit():
    """Verifica que el bucle termine cuando el usuario escribe 'salir'."""
    with patch("src.adapters.cli.app.Prompt.ask", side_effect=["salir"]), \
         patch("src.adapters.cli.app.MultiProcessManager") as mock_mcp, \
         patch("src.adapters.cli.app.SQLiteChatRepository") as mock_repo, \
         patch("src.adapters.cli.app.VertexAIAdapter"), \
         patch("src.adapters.cli.app.Orchestrator") as mock_orch:
        
        # Setup mocks
        mock_mcp_instance = mock_mcp.return_value
        mock_mcp_instance.initialize = AsyncMock()
        mock_mcp_instance.list_tools = AsyncMock(return_value=[])
        mock_mcp_instance.stop = AsyncMock()
        
        mock_repo_instance = mock_repo.return_value
        mock_repo_instance.initialize = AsyncMock()
        
        await interactive_loop()
        
        mock_mcp_instance.initialize.assert_called_once()
        mock_mcp_instance.stop.assert_called_once()

@pytest.mark.asyncio
async def test_interactive_loop_process_message():
    """Verifica que se procese un mensaje y se muestre la respuesta."""
    # Simulamos: pregunta -> salir
    with patch("src.adapters.cli.app.Prompt.ask", side_effect=["¿Hola?", "salir"]), \
         patch("src.adapters.cli.app.MultiProcessManager") as mock_mcp, \
         patch("src.adapters.cli.app.SQLiteChatRepository") as mock_repo, \
         patch("src.adapters.cli.app.OllamaAdapter"), \
         patch("src.adapters.cli.app.Orchestrator") as mock_orch:
        
        mock_orch_instance = mock_orch.return_value
        mock_orch_instance.process_message = AsyncMock(return_value="Respuesta de la IA")
        
        mock_mcp_instance = mock_mcp.return_value
        mock_mcp_instance.initialize = AsyncMock()
        mock_mcp_instance.list_tools = AsyncMock(return_value=[MagicMock()])
        mock_mcp_instance.stop = AsyncMock()
        
        mock_repo_instance = mock_repo.return_value
        mock_repo_instance.initialize = AsyncMock()
        
        await interactive_loop()
        
        mock_orch_instance.process_message.assert_called_once_with("¿Hola?", session_id=ANY)
