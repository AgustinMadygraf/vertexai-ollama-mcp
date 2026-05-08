# Technology Stack

Listado de tecnologías y bibliotecas clave utilizadas en el proyecto.

## 1. Lenguaje y Core
- **Python 3.10+**: Tipado estático y asincronía nativa.
- **FastAPI**: Para la exposición de webhooks y el endpoint de salud.
- **Pydantic**: Validación de datos y esquemas de herramientas.

## 2. Inteligencia Artificial
- **Google Cloud Vertex AI**: Modelos Gemini Pro/Flash para razonamiento complejo y tool calling robusto.
- **Ollama**: Ejecución local de LLMs (Llama 3, Mistral) para tareas de menor coste o mayor privacidad.
- **GLiNER**: Biblioteca NER (Named Entity Recognition) zero-shot extremadamente ligera para la extracción de parámetros de herramientas en el motor local.

## 3. Protocolos
- **Model Context Protocol (MCP)**: Estándar para la interacción con herramientas externas.
- **Chatwoot API**: Protocolo de mensajería para la integración con el cliente final.

## 4. Observabilidad y Monitoreo
- **Rich**: Logging enriquecido en consola para desarrollo y auditoría.
- **Loguru/Standard Logging**: Configurado para generar logs estructurados compatibles con stacks de monitoreo.
