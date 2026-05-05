# Telegram Ollama MCP

Un puente entre Telegram, Ollama y el Protocolo de Contexto de Modelo (MCP).

## Requisitos

- Python 3.10+
- Ollama instalado y corriendo
- Un Token de Bot de Telegram (vía @BotFather)

## Instalación

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configurar variables de entorno:
   ```bash
   cp .env.example .env
   # Edita el archivo .env con tus credenciales
   ```

3. Ejecutar el bot:
   ```bash
   python main.py
   ```

## Arquitectura

El proyecto sigue los principios de Clean Architecture:
- `src/entities`: Modelos de dominio.
- `src/use_cases`: Lógica de negocio (ej. procesamiento de mensajes con herramientas).
- `src/interface_adapters`: Gateways para Ollama y MCP.
- `main.py`: Punto de entrada e infraestructura de Telegram.
