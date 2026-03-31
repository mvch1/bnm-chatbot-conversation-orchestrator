import hmac
import hashlib
import httpx
from typing import Optional, Dict, Any
from config import settings


class WhatsAppHandler:
    BASE_URL = "https://graph.facebook.com/v18.0"

    def __init__(self):
        self.token    = settings.whatsapp_token
        self.phone_id = settings.whatsapp_phone_number_id
        self.client   = httpx.AsyncClient(timeout=10.0)

    def parse_incoming(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract message data from WhatsApp webhook payload."""
        try:
            entry = payload["entry"][0]["changes"][0]["value"]
            if "messages" not in entry:
                return None
            msg = entry["messages"][0]
            return {
                "from":       msg["from"],
                "message_id": msg["id"],
                "type":       msg.get("type", "text"),
                "text":       msg.get("text", {}).get("body", ""),
                "timestamp":  msg.get("timestamp"),
            }
        except (KeyError, IndexError):
            return None

    def verify_signature(self, payload_bytes: bytes, signature: str) -> bool:
        """Verify HMAC-SHA256 signature from Meta.
        Returns True if no app_secret configured (dev mode).
        """
        if not settings.whatsapp_app_secret:
            return True  # Dev mode — skip verification
        expected = "sha256=" + hmac.new(
            settings.whatsapp_app_secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    async def send_text(self, to: str, text: str):
        """Send a text message via WhatsApp Business API."""
        if not self.token or not self.phone_id:
            return  # No token configured — dev mode
        url = f"{self.BASE_URL}/{self.phone_id}/messages"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text[:4096]},
        }
        try:
            await self.client.post(url, json=payload, headers=headers)
        except Exception:
            pass

    async def mark_as_read(self, message_id: str):
        """Mark message as read."""
        if not self.token or not self.phone_id:
            return
        url = f"{self.BASE_URL}/{self.phone_id}/messages"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {"messaging_product": "whatsapp", "status": "read", "message_id": message_id}
        try:
            await self.client.post(url, json=payload, headers=headers)
        except Exception:
            pass

    async def close(self):
        await self.client.aclose()
