import pytest
from unittest.mock import patch, mock_open
from src.adapters.settings.config import load_mcp_config, AppSettings

def test_app_settings_defaults():
    settings = AppSettings()
    assert settings.log_level == "INFO"
    assert settings.debug is False

def test_load_mcp_config_success():
    yaml_content = """
    mcpServers:
      test_server:
        command: "ls"
        args: ["-la"]
    """
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            config = load_mcp_config("dummy.yaml")
            assert "test_server" in config
            assert config["test_server"].command == "ls"
            assert config["test_server"].args == ["-la"]

def test_load_mcp_config_file_not_found():
    with patch("os.path.exists", return_value=False):
        config = load_mcp_config("non_existent.yaml")
        assert config == {}
