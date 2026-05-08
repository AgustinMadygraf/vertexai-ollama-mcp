# Discovery: Research & Active Questions

Este documento registra únicamente las dudas activas y el proceso de investigación en curso. Una vez resueltas, las conclusiones deben moverse a los documentos de Arquitectura, Infraestructura o Stack Tecnológico.

## 1. Dudas Activas (Investigación en curso)

### 1.1 GLiNER y Parámetros Opcionales
- **Pregunta**: ¿Cómo maneja GLiNER las entidades que no están presentes en el texto si se definen en el esquema de la herramienta como obligatorias vs opcionales?
- **Estado**: Requiere pruebas empíricas con el motor `local-gpu`. Es crítico para evitar que el clasificador invente parámetros (*hallucinations*).

### 1.2 Benchmark de Latencia en APU (OpenVINO)
- **Pregunta**: ¿Cuál es el límite de concurrencia en el Ryzen 3400G antes de que la inferencia supere los 5 segundos?
- **Estado**: Pendiente ejecutar script de benchmark con múltiples peticiones simultáneas sobre el adaptador de Ollama y el router semántico.
