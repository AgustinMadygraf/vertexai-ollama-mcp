# Infrastructure & Environment

Detalles sobre el entorno de ejecución, hardware y túneles de comunicación.

## 1. Hardware Context
El sistema está optimizado para ejecutarse en hardware con capacidades de cómputo limitadas pero con aceleración disponible:
- **CPU/APU**: AMD Ryzen 5 3400G con Radeon Vega Graphics.
- **OS**: Ubuntu 24.04 LTS.

## 2. Aceleración de Inferencia
Para maximizar el rendimiento de la APU Ryzen sin dependencias complejas de ROCm:
- **Motor**: **OpenVINO**.
- **Uso**: Inferencia de modelos locales (NER, clasificación de intención) para minimizar la latencia.

## 3. Alta Disponibilidad (Túneles)
Se utiliza una estrategia de **Composite Infrastructure HA** para asegurar que el webhook siempre sea accesible desde Chatwoot:
- **Túnel Primario**: Cloudflare Tunnel (`cloudflared`).
- **Túnel Secundario**: ngrok (redundancia).
- **Monitoreo**: El endpoint `/health` agrega el estado de ambos túneles y recursos del sistema (CPU/RAM).

## 4. Seguridad y Validación
- **Cloudflare**: Validación de headers `CF-Ray` y `CF-Connecting-IP`.
- **ngrok**: Validación de headers `x-forwarded-for`.
- **Tokens**: Uso de `api_access_token` para la comunicación con la API de Chatwoot.
