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

## 6. Persistencia y Gestión de Estado
Se utiliza una base de datos **SQLite asíncrona** (`aiosqlite`) para mantener el estado de las sesiones de chat entre diferentes turnos de interacción.

- **Patrón de Almacenamiento**: "Borrar y Reinsertar" (Overwrite). Al finalizar cada turno, se persiste el historial completo de la sesión. Esto garantiza que el orden de los mensajes y las llamadas a herramientas sean coherentes.
- **Formato de Datos**: Las llamadas a herramientas (`tool_calls`) y sus argumentos se almacenan como estructuras JSON serializadas dentro de la tabla de mensajes, permitiendo una reconstrucción fiel del contexto para motores que requieren el historial técnico (como Gemini).
