"""
Path: src/adapters/monitoring/cloudflare_adapter.py
"""
import httpx
from src.core.domain.ports import InfrastructureMonitorPort
from src.adapters.settings.config import settings
from src.adapters.settings.logger import logger

class CloudflareMonitorAdapter(InfrastructureMonitorPort):
    def __init__(self):
        self.account_id = settings.cloudflare_account_id
        self.api_token = settings.cloudflare_api_token
        self.tunnel_id = settings.cloudflare_tunnel_id

    async def check_tunnel_status(self) -> dict:
        """Consulta el estado del túnel en la API de Cloudflare."""
        if not all([self.account_id, self.api_token, self.tunnel_id]):
            return {"status": "unconfigured", "detail": "Faltan credenciales de Cloudflare"}

        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/tunnels/{self.tunnel_id}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                status = data.get("result", {}).get("status", "unknown")
                
                logger.info(f"Estado del túnel Cloudflare: {status}")
                return {
                    "status": "healthy" if status == "healthy" else "degraded",
                    "cloudflare_status": status,
                    "tunnel_id": self.tunnel_id
                }
        except Exception as e:
            logger.error(f"Error al verificar túnel Cloudflare: {str(e)}")
            return {"status": "down", "detail": str(e)}

    def validate_request_headers(self, headers: dict) -> bool:
        """
        Valida que la petición contenga los headers de Cloudflare.
        En producción se recomienda además validar los rangos de IP.
        """
        # CF-Ray es el header más común inyectado por Cloudflare
        is_cf = "cf-ray" in headers or "x-forwarded-proto" in headers
        
        if not is_cf:
            logger.warning("Petición detectada fuera de Cloudflare (Missing CF-Ray)")
        
        return is_cf
