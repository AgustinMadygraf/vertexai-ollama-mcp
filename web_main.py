"""
Path: web_main.py
Servidor web para la integración con Chatwoot.
"""
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.adapters.mcp.process_manager import MultiProcessManager
from src.adapters.ai.local_gpu_adapter import LocalGPUAdapter
from src.core.application.orchestrator import Orchestrator
from src.adapters.chatwoot.api_adapter import ChatwootAPIAdapter
from src.adapters.chatwoot.webhook_adapter import router as chatwoot_router
from src.adapters.settings.logger import logger

# Gestión de ciclo de vida del servidor MCP
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Inicializar servidores MCP
    mcp_manager = MultiProcessManager()
    await mcp_manager.initialize()
    
    # 2. Configurar orquestador
    ai_adapter = LocalGPUAdapter()
    app.state.orchestrator = Orchestrator(ai_adapter, mcp_manager)
    app.state.chatwoot_api = ChatwootAPIAdapter()
    
    logger.info("Servidor Web MCP iniciado y motores listos.")
    
    yield
    
    # 3. Limpieza
    await mcp_manager.stop()
    logger.info("Servidores MCP detenidos.")

app = FastAPI(title="MCP Chatwoot Bridge", lifespan=lifespan)

# Registrar rutas
app.include_router(chatwoot_router)

@app.get("/")
async def root():
    return {"status": "online", "bridge": "Chatwoot-MCP"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
