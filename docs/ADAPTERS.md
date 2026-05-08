# Adapters & Integrations

Detalles específicos de los adaptadores de entrada y salida.

## 1. Chatwoot Webhook Adapter
- **Endpoint**: `POST /webhook/chatwoot`
- **Estrategia de Respuesta**: 
  - Para cumplir con el timeout de 5s, el adaptador responde `200 OK` inmediatamente después de validar la firma del webhook.
  - El procesamiento se delega al `Orchestrator` de forma asíncrona usando `asyncio.create_task`.
- **API de Salida**: Uso de `POST /api/v1/accounts/{account_id}/conversations/{conversation_id}/messages` para enviar la respuesta procesada.

## 2. MCP Client Adapter
- **Responsabilidad**: Conectar con servidores MCP (locales o remotos), descubrir herramientas y ejecutar invocaciones.
- **Transformación**: Mapea las respuestas de los servidores MCP al formato de mensaje del dominio.

## 3. AI Engine Adapters
- **VertexAIAdapter**: Gestiona la autenticación con GCP y el envío de prompts/herramientas a Gemini.
- **OllamaAdapter**: Comunicación con la API local de Ollama (puerto 11434).
