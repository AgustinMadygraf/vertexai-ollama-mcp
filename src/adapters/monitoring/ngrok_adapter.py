"""
Path: src/adapters/monitoring/ngrok_adapter.py
"""
import httpx
from src.core.domain.ports import InfrastructureMonitorPort
from src.adapters.settings.config import settings
from src.adapters.settings.logger import logger

class NgrokMonitorAdapter(InfrastructureMonitorPort):
    def __init__(self):
        self.api_url = settings.ngrok_api_url

    async def check_tunnel_status(self) -> dict:
        """Consulta el estado del túnel en la API local de ngrok."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.api_url, timeout=2.0)
                if response.status_code == 200:
                    data = response.json()
                    tunnels = data.get("tunnels", [])
                    if tunnels:
                        public_url = tunnels[0].get("public_url", "unknown")
                        logger.info(f"Túnel ngrok activo: {public_url}")
                        return {
                            "status": "healthy",
                            "provider": "ngrok",
                            "public_url": public_url,
                            "tunnel_count": len(tunnels)
                        }
                    return {"status": "degraded", "provider": "ngrok", "detail": "No hay túneles activos"}
                return {"status": "down", "provider": "ngrok", "detail": f"API respondió con {response.status_code}"}
        except Exception as e:
            # logger.debug(f"Ngrok no está corriendo: {str(e)}")
            return {"status": "inactive", "provider": "ngrok", "detail": "ngrok no detectado localmente"}

    def validate_request_headers(self, headers: dict) -> bool:
        """
        Valida que la petición contenga headers típicos de ngrok.
        """
        is_ngrok = "x-forwarded-for" in headers and "x-original-host" in headers
        
        if is_ngrok:
            logger.info("Petición validada vía ngrok")
        
        return is_ngrok
