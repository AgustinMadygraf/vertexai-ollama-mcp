# VertexAI-Ollama MCP CLI

Este proyecto es una herramienta de línea de comandos (CLI) diseñada para actuar como un puente entre potentes modelos de lenguaje (LLMs) y servidores que implementan el **Model Context Protocol (MCP)**.

Permite orquestar interacciones utilizando tanto la infraestructura en la nube de **Google Cloud Vertex AI** como modelos locales a través de **Ollama**.

## 🚀 Objetivo
Facilitar la ejecución de herramientas y el acceso a recursos expuestos por servidores MCP mediante una interfaz unificada y flexible.

## ⚙️ Configuración
1. Copia `.env.example` a `.env` y completa tus credenciales de Google Cloud.
2. Define tus servidores en `config/mcp_config.yaml`.
3. Instala las dependencias: `pip install -r requirements.txt`.

## 💻 Uso Básico
```bash
# Iniciar una sesión interactiva con Vertex AI
python3 main.py --engine vertex
```
Usa `--debug` para inspeccionar el tráfico JSON-RPC con los servidores.

## 🛠️ Tecnologías
- **Lenguaje:** Python
- **AI Engines:** Vertex AI (Gemini), Ollama, Sentence Transformers (Local GPU)
- **Protocolo:** Model Context Protocol (MCP)
- **Interfaz:** CLI (Command Line Interface) & Webhooks (Próximamente: Chatwoot)
- **Infraestructura:** Cloudflare Tunnels (Validación & Health Check)

## 📂 Estructura de Documentación
- [Discovery](docs/DISCOVERY.md): Investigación y hallazgos preliminares.
- [SRS](docs/SRS.md): Especificación de Requisitos de Software.
- [TODO](docs/TODO.md): Listado de tareas y progreso.

## ⚙️ Configuración (Próximamente)
El proyecto utilizará variables de entorno para gestionar credenciales y configuraciones de servidores MCP.
