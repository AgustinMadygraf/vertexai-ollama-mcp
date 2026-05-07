"""
Path: src/adapters/chatwoot/api_adapter.py
"""
import httpx
from src.core.domain.ports import ChatwootOutputPort
from src.adapters.settings.config import settings
from src.adapters.settings.logger import logger

class ChatwootAPIAdapter(ChatwootOutputPort):
    def __init__(self):
        self.base_url = settings.chatwoot_url
        self.api_token = settings.chatwoot_api_token

    async def send_message(self, account_id: int, conversation_id: int, content: str) -> bool:
        """Envía una respuesta a Chatwoot."""
        if not self.api_token:
            logger.error("CHATWOOT_API_TOKEN no configurado.")
            return False

        url = f"{self.base_url}/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages"
        headers = {
            "api_access_token": self.api_token,
            "Content-Type": "application/json"
        }
        payload = {
            "content": content,
            "message_type": "outgoing"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                logger.info(f"Respuesta enviada a Chatwoot (Conv: {conversation_id})")
                return True
        except Exception as e:
            logger.error(f"Error al enviar mensaje a Chatwoot: {str(e)}")
            return False
