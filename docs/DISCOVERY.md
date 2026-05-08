# Discovery: Research & Active Questions

Este documento registra únicamente las dudas activas y el proceso de investigación en curso. Una vez resueltas, las conclusiones deben moverse a los documentos de Arquitectura, Infraestructura o Stack Tecnológico.

## 1. Dudas Activas (Investigación en curso)

## 1. Dudas Activas (Investigación en curso)

### 1.1 Compatibilidad de Tool Calling en Ollama
- **Pregunta**: ¿Qué modelos locales (Llama 3, Mistral, etc.) soportan nativamente el formato de respuesta de herramientas sin necesidad de prompts de sistema complejos?
- **Estado**: Investigando modelos optimizados para *function calling* disponibles en la librería de Ollama.

### 1.2 GLiNER y Parámetros Opcionales
- **Pregunta**: ¿Cómo maneja GLiNER las entidades que no están presentes en el texto si se definen en el esquema de la herramienta como obligatorias vs opcionales?
- **Estado**: Requiere pruebas empíricas con el motor `local-gpu`.

### 1.3 Benchmark de Latencia en APU (OpenVINO)
- **Pregunta**: ¿Cuál es el límite de concurrencia en el Ryzen 3400G antes de que la inferencia supere los 5 segundos?
- **Estado**: Pendiente ejecutar script de benchmark con múltiples peticiones simultáneas.

### 1.4 Persistencia de Historial con Herramientas
- **Pregunta**: ¿Cómo estructurar la tabla de `Messages` en SQLite para almacenar no solo el texto, sino el `call_id` y el `result` de las herramientas MCP para mantener la coherencia del contexto en Gemini/Ollama?
- **Estado**: Diseño de esquema de base de datos en fase preliminar.

## 2. Historial de Resoluciones
- **Mapeo de Esquemas MCP a Vertex AI**: Resuelto mediante el `SchemaMapper` en `VertexAIAdapter`. Gemini ahora puede recibir herramientas dinámicas y procesar sus respuestas siguiendo el ciclo completo de FunctionCall/Response.
- **Chatwoot API**: Confirmado el uso de webhooks asíncronos para evitar timeouts. (Conclusión movida a `docs/ADAPTERS.md`).
- **HA Infraestructura**: ngrok integrado como redundancia exitosamente. (Conclusión movida a `docs/INFRASTRUCTURE.md`).
