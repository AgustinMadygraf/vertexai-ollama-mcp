# TODO: Roadmap de Implementación

## Fase 1: Cimientos y Documentación 🏗️
- [x] Estructura inicial de documentación (SRS, Discovery, TODO).
- [x] Definición de Arquitectura Hexagonal y DDD.
- [x] Diseño de configuración híbrida (YAML + .env).
- [x] Selección de stack tecnológico (Python 3.10+, SDK MCP).
- [x] Creación de estructura de directorios (.gitkeep).

## Fase 2: Implementación Core & Adapters 🔌
- [x] Estructura de carpetas y archivos base (`__init__.py`).
- [ ] Implementación de `SemanticRouterAdapter` (Local-GPU / OpenVINO).
- [ ] Definición de Puertos (Interfaces) adaptados para clasificación rápida.
- [ ] Modelado de Dominio: `Intent`, `ToolCall`, `ToolResult`.
- [ ] Modelado de Dominio: `ChatSession` (efímera), `Message`, `Tool`.
- [ ] Implementación de `MultiProcessManager` (Arranque masivo automático).
- [ ] Implementación de `Typer` CLI (Bucle REPL interactivo).
- [ ] Sistema de logs separado (File-based para evitar ensuciar el REPL).

## Fase 3: Integración de Modelos 🧠
- [ ] Adaptador para Vertex AI Gateway.
- [ ] Adaptador para Ollama Gateway.
- [ ] Lógica de orquestación (Agent Loop).

## Fase 4: UX y CLI 💻
- [ ] Implementación de comandos `list-tools`, `chat`, `run`.
- [ ] Manejo de errores y logs visuales (Rich/Typer).

## Fase 5: Testing y Refinamiento 🧪
- [ ] Unit testing de los Gateways.
- [ ] Mocking de servidores MCP para integración.

## Fase 6: Escalabilidad y Webhooks (Chatwoot) 🌐
- [x] Implementación de servidor FastAPI para Webhooks.
- [x] Adaptador de Entrada: `ChatwootWebhookAdapter`.
- [x] Adaptador de Salida: `ChatwootAPIAdapter` (para enviar respuestas).
- [x] Refactor de `Orchestrator` para soporte multi-sesión con persistencia.
- [x] Implementación de validación de firma HMAC (X-Chatwoot-Signature).
- [ ] Integración de **GLiNER** en `LocalGPUAdapter` para extracción de argumentos real.
