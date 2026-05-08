# Discovery: Research & Active Questions

Este documento registra únicamente las dudas activas y el proceso de investigación en curso. Una vez resueltas, las conclusiones deben moverse a los documentos de Arquitectura, Infraestructura o Stack Tecnológico.

## 1. Dudas Activas (Investigación en curso)

### 1.1 Mapeo de Esquemas MCP a Vertex AI
- **Pregunta**: ¿Cómo transformar dinámicamente las definiciones de herramientas (JSON Schema) de los servidores MCP al formato `Function Declaration` que requiere el SDK de Vertex AI para Python?
- **Estado**: Pendiente de implementación de un `SchemaMapper` en el adaptador de Vertex AI.

### 1.2 Compatibilidad de Tool Calling en Ollama
- **Pregunta**: ¿Qué modelos locales (Llama 3, Mistral, etc.) soportan nativamente el formato de respuesta de herramientas sin necesidad de prompts de sistema complejos?
- **Estado**: Investigando modelos optimizados para *function calling* disponibles en la librería de Ollama.

### 1.3 GLiNER y Parámetros Opcionales
- **Pregunta**: ¿Cómo maneja GLiNER las entidades que no están presentes en el texto si se definen en el esquema de la herramienta como obligatorias vs opcionales?
- **Estado**: Requiere pruebas empíricas con el motor `local-gpu`.

### 1.4 Benchmark de Latencia en APU (OpenVINO)
- **Pregunta**: ¿Cuál es el límite de concurrencia en el Ryzen 3400G antes de que la inferencia supere los 5 segundos?
- **Estado**: Pendiente ejecutar script de benchmark con múltiples peticiones simultáneas.

### 1.5 Persistencia de Historial con Herramientas
- **Pregunta**: ¿Cómo estructurar la tabla de `Messages` en SQLite para almacenar no solo el texto, sino el `call_id` y el `result` de las herramientas MCP para mantener la coherencia del contexto en Gemini/Ollama?
- **Estado**: Diseño de esquema de base de datos en fase preliminar.

## 2. Historial de Resoluciones
*(Cuando una duda se resuelva, mover el resumen aquí antes de archivarla en la documentación permanente)*
- **Chatwoot API**: Confirmado el uso de webhooks asíncronos para evitar timeouts. (Conclusión movida a `docs/ADAPTERS.md`).
- **HA Infraestructura**: ngrok integrado como redundancia exitosamente. (Conclusión movida a `docs/INFRASTRUCTURE.md`).
