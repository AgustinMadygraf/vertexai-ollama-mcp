"""
Path: src/adapters/settings/logger.py
"""
import logging
import os
from src.adapters.settings.config import settings

def setup_logger():
    """Configura el sistema de logs para que escriba en archivos y no en consola."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "app.log")
    
    # Configuramos el logger de la aplicación
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
        ]
    )
    
    # Silenciamos logs de librerías externas que pueden ser ruidosos
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    
    return logging.getLogger("mcp-cli")

# Exportamos una instancia lista para usar
logger = setup_logger()
