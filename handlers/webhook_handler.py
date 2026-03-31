from fastapi import Request, HTTPException
from config import settings


async def verify_webhook(mode: str, token: str, challenge: str) -> str:
    """Handle GET webhook verification from Meta."""
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        return challenge
    raise HTTPException(status_code=403, detail="Verification failed")
