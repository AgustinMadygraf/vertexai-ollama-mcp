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
- **Async/Await**: Uso intensivo de asincronía para la gestión de subprocesos MCP concurrentes.
