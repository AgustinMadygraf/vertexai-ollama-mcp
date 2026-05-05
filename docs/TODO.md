# TODO: Roadmap de Implementación

## Fase 1: Cimientos y Documentación 🏗️
- [x] Estructura inicial de documentación.
- [x] Definición de requisitos multi-server y debug.
- [ ] Configuración de entorno virtual y dependencias básicas.

## Fase 2: Implementación Core & Adapters 🔌
- [ ] Estructura de carpetas: `src/core` (Domain/Application) y `src/adapters` (CLI/AI/MCP).
- [ ] Definición de Puertos (Interfaces) para `AIEngine` y `MCPClient`.
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
