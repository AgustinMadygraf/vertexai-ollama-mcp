"""
Path: src/adapters/settings/config.py
"""
import os
import yaml
from typing import Dict, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class McpServerConfig(BaseSettings):
    command: str
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)

class AppSettings(BaseSettings):
    # Google Cloud / Vertex AI (Postponed but kept for structure)
    google_cloud_project: Optional[str] = Field(None, alias="GOOGLE_CLOUD_PROJECT")
    google_cloud_location: Optional[str] = Field("us-central1", alias="GOOGLE_CLOUD_LOCATION")
    
    # Ollama (Postponed but kept for structure)
    ollama_base_url: str = Field("http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field("llama3", alias="OLLAMA_MODEL")
    
    # Local GPU / OpenVINO
    local_gpu_model_name: str = Field("all-MiniLM-L6-v2", alias="LOCAL_GPU_MODEL_NAME")
    
    # Application Logic
    debug: bool = Field(False, alias="DEBUG")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

def load_mcp_config(config_path: str = "config/mcp_config.yaml") -> Dict[str, McpServerConfig]:
    """Carga la definición de los servidores MCP desde el archivo YAML."""
    if not os.path.exists(config_path):
        return {}
    
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    servers_data = data.get("mcpServers", {})
    return {name: McpServerConfig(**cfg) for name, cfg in servers_data.items()}

# Instancia global para ser inyectada
settings = AppSettings()
