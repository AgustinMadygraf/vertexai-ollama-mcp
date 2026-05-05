# VertexAI-Ollama MCP CLI

Este proyecto es una herramienta de línea de comandos (CLI) diseñada para actuar como un puente entre potentes modelos de lenguaje (LLMs) y servidores que implementan el **Model Context Protocol (MCP)**.

Permite orquestar interacciones utilizando tanto la infraestructura en la nube de **Google Cloud Vertex AI** como modelos locales a través de **Ollama**.

## 🚀 Objetivo
Facilitar la ejecución de herramientas y el acceso a recursos expuestos por servidores MCP mediante una interfaz unificada y flexible.

## 💻 Uso Básico
```bash
# Iniciar una sesión interactiva
python3 main.py --engine [vertex|ollama]
```
Una vez dentro de la sesión, los servidores MCP permanecerán activos para consultas instantáneas. Usa `--debug` para ver el tráfico JSON-RPC.

## 🛠️ Tecnologías
- **Lenguaje:** Python
- **AI Engines:** Vertex AI (Gemini), Ollama
- **Protocolo:** Model Context Protocol (MCP)
- **Interfaz:** CLI (Command Line Interface)

## 📂 Estructura de Documentación
- [Discovery](docs/DISCOVERY.md): Investigación y hallazgos preliminares.
- [SRS](docs/SRS.md): Especificación de Requisitos de Software.
- [TODO](docs/TODO.md): Listado de tareas y progreso.

## ⚙️ Configuración (Próximamente)
El proyecto utilizará variables de entorno para gestionar credenciales y configuraciones de servidores MCP.
