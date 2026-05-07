"""
Path: src/adapters/chatwoot/webhook_adapter.py
"""
import hmac
import hashlib
from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks
from src.core.application.orchestrator import Orchestrator
from src.core.domain.ports import ChatwootOutputPort
from src.adapters.settings.config import settings
from src.adapters.settings.logger import logger

router = APIRouter()

def verify_signature(body: bytes, signature: str) -> bool:
    """Verifica la firma HMAC-SHA256 de Chatwoot."""
    if not settings.chatwoot_webhook_secret:
        return True # Si no hay secreto, no verificamos (desaconsejado en producción)
    
    digest = hmac.new(
        settings.chatwoot_webhook_secret.encode(),
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(digest, signature)

async def process_and_reply(
    payload: dict, 
    orchestrator: Orchestrator, 
    output_adapter: ChatwootOutputPort
):
    """Procesa el mensaje de forma asíncrona y envía la respuesta."""
    try:
        content = payload.get("content")
        conversation_id = payload.get("conversation", {}).get("display_id")
        account_id = payload.get("account", {}).get("id")
        
        if not content or not conversation_id or not account_id:
            logger.warning("Payload de Chatwoot incompleto.")
            return

        # Solo procesamos mensajes entrantes
        if payload.get("message_type") != "incoming":
            return

        # 1. Ejecutar lógica del orquestador
        response_text = await orchestrator.process_message(content, session_id=f"chatwoot-{conversation_id}")
        
        # 2. Enviar respuesta vía API
        await output_adapter.send_message(account_id, conversation_id, response_text)

    except Exception as e:
        logger.error(f"Error en el procesamiento asíncrono de Chatwoot: {str(e)}", exc_info=True)

@router.post("/webhooks/chatwoot")
async def chatwoot_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_chatwoot_signature: str = Header(None)
):
    """Endpoint principal para recibir webhooks de Chatwoot."""
    # 1. Validar que la petición venga de un túnel autorizado (Cloudflare/ngrok)
    infra_monitor = request.app.state.infra_monitor
    if not infra_monitor.validate_request_headers(dict(request.headers)):
        logger.warning("Acceso denegado: Petición no proviene de un túnel autorizado.")
        raise HTTPException(status_code=403, detail="Access denied: Requests must come through an authorized tunnel")

    # 2. Validar firma de Chatwoot
    body = await request.body()
    if x_chatwoot_signature and not verify_signature(body, x_chatwoot_signature):
        logger.warning("Firma de Chatwoot inválida.")
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    
    orchestrator = request.app.state.orchestrator
    output_adapter = request.app.state.chatwoot_api
    
    background_tasks.add_task(process_and_reply, payload, orchestrator, output_adapter)
    
    return {"status": "accepted"}
