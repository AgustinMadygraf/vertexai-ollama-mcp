"""
Path: web_main.py
Servidor web para la integración con Chatwoot con Observabilidad Avanzada.
"""
import time
import psutil
import uvicorn
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.adapters.mcp.process_manager import MultiProcessManager
from src.adapters.ai.local_gpu_adapter import LocalGPUAdapter
from src.core.application.orchestrator import Orchestrator
from src.adapters.chatwoot.api_adapter import ChatwootAPIAdapter
from src.adapters.monitoring.cloudflare_adapter import CloudflareMonitorAdapter
from src.adapters.chatwoot.webhook_adapter import router as chatwoot_router
from src.adapters.settings.logger import logger

console = Console()

def print_logo():
    """Imprime un logo estético al arrancar."""
    console.print(Panel.fit(
        "[bold cyan]MCP BRIDGE[/bold cyan] [bold white]v1.1.0[/bold white]\n"
        "[dim]High-Performance Semantic Routing & Observability[/dim]",
        border_style="cyan"
    ))

@asynccontextmanager
async def lifespan(app: FastAPI):
    print_logo()
    
    # 1. Inicializar servidores MCP
    mcp_manager = MultiProcessManager()
    with console.status("[bold green]Iniciando servidores MCP...") as status:
        await mcp_manager.initialize()
    
    # 2. Configurar orquestador y adaptadores
    ai_adapter = LocalGPUAdapter()
    app.state.orchestrator = Orchestrator(ai_adapter, mcp_manager)
    app.state.chatwoot_api = ChatwootAPIAdapter()
    app.state.infra_monitor = CloudflareMonitorAdapter()
    app.state.mcp_manager = mcp_manager
    
    logger.info("[bold green]✓[/bold green] Sistema de orquestación listo.")
    
    yield
    
    # 3. Limpieza
    await mcp_manager.stop()
    logger.info("[bold yellow]![/bold yellow] Servidores MCP detenidos.")

app = FastAPI(title="MCP Chatwoot Bridge", lifespan=lifespan)

# Middleware de Observabilidad: Tiempo de respuesta y logging estético
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    color = "green" if response.status_code < 400 else "red"
    logger.info(
        f"[{color}]{request.method}[/{color}] {request.url.path} "
        f"- [bold]{response.status_code}[/bold] "
        f"({process_time:.4f}s)"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Registrar rutas
app.include_router(chatwoot_router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "bridge": "Chatwoot-MCP",
        "version": "1.1.0"
    }

@app.get("/health")
async def health_check(request: Request):
    """
    Agregador de salud del sistema con métricas detalladas.
    """
    # 1. Estado de Cloudflare
    monitor = request.app.state.infra_monitor
    cf_status = await monitor.check_tunnel_status()
    
    # 2. Estado de Servidores MCP
    mcp_manager = request.app.state.mcp_manager
    active_sessions = list(mcp_manager.sessions.keys())
    
    # 3. Recursos del Sistema
    mem = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent()
    
    health_status = "ok"
    if cf_status["status"] != "healthy" or not active_sessions:
        health_status = "warning"

    return {
        "status": health_status,
        "timestamp": time.time(),
        "infrastructure": {
            "cloudflare": cf_status,
            "system": {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": mem.percent,
                "memory_available_mb": mem.available / (1024 * 1024)
            }
        },
        "services": {
            "mcp_bridge": {
                "status": "active" if active_sessions else "inactive",
                "active_servers": active_sessions,
                "server_count": len(active_sessions)
            },
            "ai_engine": "local-gpu (ready)"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
