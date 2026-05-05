import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from src.adapters.ai.local_gpu_adapter import LocalGPUAdapter
from src.core.domain.entities import ToolDefinition

@pytest.fixture
def mock_transformer():
    with patch("src.adapters.ai.local_gpu_adapter.SentenceTransformer") as mock:
        yield mock

def test_local_gpu_init(mock_transformer):
    adapter = LocalGPUAdapter()
    mock_transformer.assert_called_once()

@pytest.mark.asyncio
async def test_classify_intent_success(mock_transformer):
    instance = mock_transformer.return_value
    instance.encode.return_value = MagicMock()
    
    with patch("src.adapters.ai.local_gpu_adapter.util.cos_sim") as mock_sim:
        # Mockeamos el objeto de retorno para que sea subscriptable y tenga .item()
        mock_score = MagicMock()
        mock_score.item.return_value = 0.9
        
        mock_sim_result = MagicMock()
        mock_sim_result.__getitem__.return_value = mock_score
        mock_sim.return_value = [mock_sim_result]
        
        # Mock np.argmax para que devuelva el índice 0
        with patch("numpy.argmax", return_value=0):
            adapter = LocalGPUAdapter()
            tools = [ToolDefinition(name="t1", description="d1", input_schema={}, server_name="s1")]
            
            result = await adapter.classify_intent("query", tools)
            
            assert result.tool_name == "t1"
            assert result.confidence == 0.9

@pytest.mark.asyncio
async def test_classify_intent_low_confidence(mock_transformer):
    instance = mock_transformer.return_value
    instance.encode.return_value = MagicMock()
    
    with patch("src.adapters.ai.local_gpu_adapter.util.cos_sim") as mock_sim:
        mock_score = MagicMock()
        mock_score.item.return_value = 0.1
        
        mock_sim_result = MagicMock()
        mock_sim_result.__getitem__.return_value = mock_score
        mock_sim.return_value = [mock_sim_result]
        
        with patch("numpy.argmax", return_value=0):
            adapter = LocalGPUAdapter()
            tools = [ToolDefinition(name="t1", description="d1", input_schema={}, server_name="s1")]
            
            result = await adapter.classify_intent("query", tools)
            assert result.confidence == 0.1
