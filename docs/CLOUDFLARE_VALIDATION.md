# Cloudflare Validation Contract & Plan

Este documento describe la estrategia para validar la integridad de la conexión a través de Cloudflare en nuestro puente MCP.

## 1. Objetivos de Validación
1.  **Integridad del Tráfico**: Asegurar que las peticiones entrantes provengan realmente de Cloudflare (vía headers `CF-Ray` y `CF-Connecting-IP`).
2.  **Estado del Túnel**: Verificar proactivamente si el túnel `cloudflared` está en estado `healthy` mediante la API de Cloudflare.
3.  **Seguridad**: Bloquear o alertar si se detectan accesos directos que evaden el proxy de Cloudflare.

## 2. Contrato del Puerto (`InfrastructureMonitorPort`)

```python
class InfrastructureMonitorPort(ABC):
    @abstractmethod
    async def check_tunnel_status(self) -> dict:
        """Verifica el estado de salud del túnel en la API de Cloudflare."""
        pass

    @abstractmethod
    def validate_request_headers(self, headers: dict) -> bool:
        """Valida si los headers de una petición entrante son consistentes con Cloudflare."""
        pass
```

## 3. Implementación del Adaptador
- **Tecnología**: `httpx` para llamadas a la API de Cloudflare.
- **Configuración**: Requiere `CLOUDFLARE_ACCOUNT_ID` y `CLOUDFLARE_API_TOKEN`.
- **Lógica de Headers**:
    - Verificar presencia de `CF-Ray`.
    - (Opcional) Validar que la IP de origen esté en el rango oficial de Cloudflare.

## 4. Integración en el Flujo
- El `ChatwootWebhookAdapter` invocará `validate_request_headers` antes de procesar cualquier webhook.
- Se expondrá un endpoint `/health` en `web_main.py` que incluirá el resultado de `check_tunnel_status`.

---

## 5. Auditoría SOLID/Hexagonal para esta Función
- **S (SRP)**: La validación de red se delega a un adaptador específico, no ensucia el orquestador.
- **D (DIP)**: El adaptador de webhook depende de `InfrastructureMonitorPort`, no de la implementación de Cloudflare.
- **Observabilidad**: Los fallos de validación de headers se registrarán como `WARNING` en los logs para detectar intentos de bypass.
