"""
Path: src/adapters/settings/logger.py
"""
import logging
import os
from rich.logging import RichHandler
from src.adapters.settings.config import settings

def setup_logger():
    """Configura el sistema de logs con Rich para consola y FileHandler para persistencia."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "server.log")
    
    # Handlers
    console_handler = RichHandler(
        rich_tracebacks=True, 
        markup=True,
        show_path=False
    )
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    
    # Configuración base
    logging.basicConfig(
        level=settings.log_level,
        format="%(message)s",
        handlers=[console_handler, file_handler]
    )
    
    # Silenciamos logs de librerías externas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    
    return logging.getLogger("mcp-bridge")

# Exportamos una instancia lista para usar
logger = setup_logger()
