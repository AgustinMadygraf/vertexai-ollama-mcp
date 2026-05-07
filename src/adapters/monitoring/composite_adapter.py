"""
Path: src/adapters/monitoring/composite_adapter.py
"""
from typing import List
from src.core.domain.ports import InfrastructureMonitorPort
from src.adapters.monitoring.cloudflare_adapter import CloudflareMonitorAdapter
from src.adapters.monitoring.ngrok_adapter import NgrokMonitorAdapter
from src.adapters.settings.logger import logger

class CompositeMonitorAdapter(InfrastructureMonitorPort):
    """
    Agregador de adaptadores de infraestructura para soportar múltiples túneles (HA).
    """
    def __init__(self):
        self.adapters: List[InfrastructureMonitorPort] = [
            CloudflareMonitorAdapter(),
            NgrokMonitorAdapter()
        ]

    async def check_tunnel_status(self) -> dict:
        """Consolida el estado de todos los túneles."""
        results = []
        overall_healthy = False
        
        for adapter in self.adapters:
            status = await adapter.check_tunnel_status()
            results.append(status)
            if status.get("status") == "healthy":
                overall_healthy = True
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "tunnels": results,
            "total_active": sum(1 for r in results if r.get("status") == "healthy")
        }

    def validate_request_headers(self, headers: dict) -> bool:
        """Valida si la petición viene de CUALQUIERA de los túneles autorizados."""
        for adapter in self.adapters:
            if adapter.validate_request_headers(headers):
                return True
        
        logger.warning("Acceso denegado: Headers no coinciden con ningún túnel autorizado.")
        return False
