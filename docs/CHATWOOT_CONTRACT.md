# Chatwoot Webhook Contract

Este documento define el contrato de comunicación entre Chatwoot y nuestro servicio de orquestación MCP.

## 1. Webhook Incoming (Chatwoot -> Orchestrator)

El servicio debe exponer un endpoint POST (ej. `/webhooks/chatwoot`).

### Payload Esperado (Evento: `message_created`)
```json
{
  "event": "message_created",
  "account": {
    "id": 1
  },
  "conversation": {
    "display_id": 123
  },
  "content": "Listame las facturas del cliente 456",
  "message_type": "incoming"
}
```

### Seguridad
- **Header**: `X-Chatwoot-Signature`
- **Método**: HMAC-SHA256 utilizando el `webhook_secret` configurado en Chatwoot.
- **Validación**: Comparar la firma con el body raw del request.

---

## 2. API Outgoing (Orchestrator -> Chatwoot)

Para responder al usuario, el servicio utilizará la API de Chatwoot.

### Endpoint
`POST /api/v1/accounts/{account_id}/conversations/{conversation_id}/messages`

### Headers
- `api_access_token`: {TOKEN_CONFIGURADO}
- `Content-Type`: `application/json`

### Payload de Respuesta
```json
{
  "content": "Resultado del servidor MCP: ...",
  "private": false
}
```

---

## 3. Consideraciones de Escalabilidad
- **Timeout**: Chatwoot espera respuesta en < 5s. El orquestador debe responder el webhook inmediatamente (200 OK) y procesar la lógica de forma asíncrona.
- **Concurrencia**: Cada `conversation.display_id` debe mapearse a una `ChatSession` en nuestro core para mantener el historial si es necesario.
- **Persistencia**: Se recomienda el uso de SQLite o Redis para mantener el estado de las sesiones entre reinicios del adaptador de webhook.
