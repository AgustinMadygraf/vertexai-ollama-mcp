# Discovery: VertexAI-Ollama MCP CLI

Este documento registra el proceso de investigación y descubrimiento de las tecnologías clave para el proyecto.

## 1. Model Context Protocol (MCP)
- **¿Qué es?**: Un estándar abierto que permite a los modelos de IA interactuar con herramientas y datos externos de manera segura.
- **Componentes clave**:
  - Servidores: Exponen herramientas y recursos.
  - Clientes: Consumen las herramientas (nuestro proyecto).

## 2. Google Cloud Vertex AI
- **Foco**: Uso de modelos Gemini Pro/Flash.
- **Integración**: Utilizar el SDK de Vertex AI para Python.
- **Tool Calling**: Investigar cómo pasar las definiciones de herramientas de MCP al formato esperado por Vertex AI.

## 3. Ollama
- **Foco**: Ejecución local de LLMs (Llama 3, Mistral, etc.).
- **Integración**: API local (usualmente puerto 11434).
- **Tool Calling**: Evaluar la compatibilidad de modelos locales con la invocación de herramientas dinámicas.

## 4. Patrones de Integración
- **Arquitectura Hexagonal (Puertos y Adaptadores)**: Se ha seleccionado esta arquitectura para desacoplar el núcleo de la lógica (Core) de las tecnologías externas (Vertex AI, Ollama, MCP).
- **Domain-Driven Design (DDD)**: Aplicado en el Core para modelar las entidades de chat y herramientas con un lenguaje ubicuo.
- **Async/Await & Python 3.10+**: Uso intensivo de asincronía y tipado moderno.
- **Estrategia Local-First (GPU)**: Priorización de modelos de clasificación locales sobre GPU para minimizar latencia y coste.
- **Hardware Detectado**: AMD Ryzen 5 3400G con Radeon Vega Graphics (Ubuntu 24.04).
- **Inferencia**: Selección de **OpenVINO** como motor de aceleración para maximizar la APU Ryzen sin dependencias complejas de ROCm.

## 5. Auditoría de Arquitectura (SOLID, DDD, Hexagonal)
- **SOLID**: El sistema cumple con la Inversión de Dependencias (DIP) mediante el uso de Puertos. El `Orchestrator` es agnóstico a la implementación de los motores de IA y clientes MCP.
- **DDD**: Existe una separación clara de entidades de dominio. El `ChatSession` y `Message` permiten modelar el flujo conversacional, aunque actualmente la CLI es mayoritariamente stateless por mensaje.
- **Hexagonal**: La estructura de carpetas (`src/core` vs `src/adapters`) refleja correctamente el patrón. Los puertos definidos en `ports.py` actúan como el contrato del dominio.
- **Observability**: Implementada mediante logs basados en archivos. Se detecta la necesidad de logs estructurados (JSON) para facilitar la integración con stacks de monitoreo cuando se escale a Webhooks.

## 6. Hallazgos y Despeje de Dudas (Chatwoot & Extracción)
- **Extracción de Argumentos**: Se ha identificado **GLiNER** como una biblioteca de extracción de entidades (NER) zero-shot extremadamente ligera y potente, ideal para el motor `local-gpu`. Permite extraer parámetros definidos en tiempo de ejecución sin un LLM completo.
- **API de Chatwoot**: Confirmado el uso de `POST /api/v1/accounts/{account_id}/conversations/{conversation_id}/messages` para enviar respuestas. Se requiere un `api_access_token`.
- **Estrategia de Respuesta Asíncrona**: Para cumplir con el timeout de 5s, el adaptador de webhook debe delegar el procesamiento al `Orchestrator` de forma asíncrona (ej. mediante `asyncio.create_task` o una cola de tareas) y responder `200 OK` al instante.
- **Documentación de Contrato**: Se ha creado `docs/CHATWOOT_CONTRACT.md` para formalizar el acuerdo entre el adaptador de entrada y la lógica de negocio, siguiendo las mejores prácticas de Arquitectura Hexagonal.

## 7. Próximos Pasos de Investigación
- Evaluar el modelo `gliner_small-v2.1` para ejecución en la APU Ryzen 3400G.
- Investigar la persistencia de `ChatSession` usando SQLite para mantener el contexto en Chatwoot.

## 8. Monitoreo de Infraestructura (Cloudflare & ngrok)
- **Estrategia de Alta Disponibilidad (HA)**: Se ha incorporado **ngrok** como túnel secundario/redundante. Esto permite mantener la conectividad si Cloudflare presenta degradación o problemas de configuración.
- **Validación de Headers**: Además de `CF-Ray` para Cloudflare, se validan headers específicos de ngrok como `x-forwarded-for` para asegurar el origen de las peticiones.
- **API de Tunnels**:
  - Cloudflare: `GET /accounts/{account_id}/tunnels` para estado global.
  - ngrok: `GET http://localhost:4040/api/tunnels` para monitoreo local dinámico.
- **Arquitectura de Salud**: El "Health Aggregator" ahora soporta múltiples proveedores de túnel, reportando un estado consolidado en el endpoint `/health`.
