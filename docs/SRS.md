# Software Requirements Specification (SRS)

## 1. Introducción
El sistema permitirá a un usuario interactuar con servidores MCP a través de una CLI interactiva (REPL), utilizando un motor de clasificación semántica local (OpenVINO) para ejecutar herramientas de forma instantánea.

## 2. Requisitos Funcionales
- **RF01: Soporte de Motores de IA**: El motor principal es `local-gpu` (Router semántico local).
- **RF02: Orquestación Multiserver Automática**: El sistema intenta encender todos los servidores configurados al inicio de la sesión.
- **RF03: Sesión Interactiva (REPL)**: Ejecución inmediata de herramientas basada en la intención del usuario.
- **RF04: Resolución de Herramientas**: Mapeo y enrutamiento dinámico hacia subprocesos activos.
- **RF05: Conectividad stdio**: Transporte concurrente mediante entrada/salida estándar.
- **RF06: Streaming**: (Opcional) Soporte para respuestas progresivas.
- **RF07: Integración con Chatwoot**: El sistema debe poder recibir mensajes vía Webhook desde Chatwoot y responder utilizando su API.
- **RF08: Gestión de Sesiones Persistentes**: El sistema debe mantener el historial de conversación por `conversation_id` de Chatwoot.
- **RF09: Validación de Infraestructura (Cloudflare)**: El sistema debe verificar que las peticiones web provengan de Cloudflare y monitorear el estado del túnel.

## 3. Requisitos No Funcionales
- **RNF01: Arquitectura Hexagonal**: Separación estricta entre Core y Adaptadores.
- **RNF02: Domain-Driven Design**: Modelado del dominio (Session, Message, Tool).
- **RNF03: Observabilidad**: Los logs técnicos se guardan en archivos (`logs/`); la pantalla se reserva para el chat y alertas críticas mediante `Rich`. El modo `--debug` activa la visualización de tráfico en consola.
- **RNF04: Seguridad**: Gestión de secretos y variables de entorno por servidor.
- **RNF05: Robustez**: Cierre seguro de todos los subprocesos al finalizar la sesión.
- **RNF06: Configuración Híbrida**: Servidores definidos en `config/mcp_config.yaml` y secretos en `.env`.
- **RNF07: Runtime**: Compatibilidad con Python 3.10 o superior (requerido por el SDK de MCP).
- **RNF08: Alta Disponibilidad y Escala**: El sistema debe soportar procesamiento asíncrono para manejar múltiples webhooks concurrentes.
- **RNF09: Seguridad de Webhooks**: Validación de firmas HMAC para peticiones entrantes de Chatwoot.
- **RNF10: Monitoreo de Red**: El sistema debe exponer un estado de salud (Health Check) que incluya la conectividad de los servidores MCP y el túnel Cloudflare.

## 4. Casos de Uso
1. **Chat con Herramientas**: El usuario inicia una sesión y realiza múltiples consultas que requieren herramientas de diversos servidores.
2. **Diagnóstico Técnico**: Inspección de la comunicación con los servidores MCP para desarrollo y personalización.
