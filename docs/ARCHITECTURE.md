# Architecture: VertexAI-Ollama MCP CLI

Este documento describe los principios y patrones arquitectónicos que rigen el proyecto.

## 1. Arquitectura Hexagonal (Puertos y Adaptadores)
Se ha seleccionado esta arquitectura para desacoplar el núcleo de la lógica (Core) de las tecnologías externas (Vertex AI, Ollama, MCP).

- **Core**: Contiene la lógica de negocio, casos de uso y modelos de dominio. Es independiente de frameworks y bibliotecas externas.
- **Puertos (`src/core/ports.py`)**: Interfaces que definen los contratos para interactuar con el mundo exterior.
- **Adaptadores (`src/adapters/`)**: Implementaciones concretas de los puertos (ej. `VertexAIAdapter`, `ChatwootWebhookAdapter`).

## 2. Domain-Driven Design (DDD)
Aplicado en el Core para modelar las entidades de chat y herramientas con un lenguaje ubicuo.

- **Entidades**: `ChatSession`, `Message`, `ToolDefinition`.
- **Agregados**: La sesión de chat actúa como raíz para gestionar el historial y el contexto de herramientas.

## 3. Principios SOLID
- **Inversión de Dependencias (DIP)**: El `Orchestrator` (caso de uso) depende de abstracciones (Puertos), no de implementaciones concretas.
- **Responsabilidad Única (SRP)**: Cada adaptador tiene una única responsabilidad (ej. validar headers de Cloudflare vs. procesar mensajes de Chatwoot).

## 4. Patrones de Diseño
- **Composite Adapter**: Utilizado para manejar múltiples túneles de infraestructura (Cloudflare + ngrok) de forma transparente para el sistema.
- **Factory Pattern**: Para la instanciación dinámica de motores de IA basados en la configuración de la intención (local vs. cloud).

## 5. Estrategia de Concurrencia
Uso intensivo de **Async/Await (Python 3.10+)** para manejar I/O no bloqueante, especialmente en la comunicación con servidores MCP y webhooks externos.
