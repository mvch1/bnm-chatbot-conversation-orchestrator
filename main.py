import uuid
import httpx

import hmac
import hashlib

from typing import Optional
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel

from config import settings
from core.session_manager import SessionManager
from core.message_router import route_message
from handlers.whatsapp_handler import WhatsAppHandler
from shared.utils.logger import get_logger
from database.repository import save_message, save_intent_message, get_or_create_user
from core.message_router import _get_recent_messages
from database.models import Session

logger = get_logger("conversation-orchestrator")


# Singletons initialisés au démarrage
_session_mgr: Optional[SessionManager] = None
_wa: Optional[WhatsAppHandler] = None



from contextlib import asynccontextmanager
VERIFY_TOKEN="testtoken123"
WHATSAPP_TOKEN="EAAUz384Y1HQBRfZCFD8DfaNS82ishtLZATYcj9LZBTFccyE6q3fwDZC66ZB8xTUnFDYRVVxwqQ1LYJ3hgEBfLwaPslkNlE3BrOHsp7hJWBu9aTaCbHdQYOOwv7G9aUDh2o4FNd5jp67zKgH3WfwC5KZAwXEa6zYjeUZAuOgFYVteiIfLtZCDGIY8LupTe2PVnq31ENI1TQJwa1yN8x5aZAMOZAX5zDo79UPW2ahM5cz2lic7jJGGDOvwl8GOXtzxJ0ZC0vdHLYl2vc82jTGFeD5KvsW"
PHONE_ID       = "1016247598244059"
BASE_URL       = "https://graph.facebook.com/v18.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global _session_mgr, _wa
    _session_mgr = SessionManager()
    _wa = WhatsAppHandler()
    logger.info("Conversation Orchestrator started")
    yield
    # Shutdown
    if _wa:
        await _wa.close()

app = FastAPI(title="Conversation Orchestrator", version="1.0.0", lifespan=lifespan)


# ── Health ────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "conversation-orchestrator"}


# ── Webhook verification (GET) ────────────────────────────
@app.get("/webhook")
async def verify_webhook(request: Request):

    params = request.query_params

    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge"))

    return "Verification failed"

# ── Webhook receive (POST) ────────────────────────────────
@app.post("/webhook")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    """Receive WhatsApp messages from Meta."""
    try:
        payload = await request.json()
    except Exception:
        return PlainTextResponse("Bad Request", status_code=400)

    # Signature check (skipped if no APP_SECRET)
    if  verify_signature(await request.body(), request.headers.get("X-Hub-Signature-256", "")):
        return PlainTextResponse("Forbidden", status_code=403)
    phone=payload.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0].get("from", "unknown")   
    message=payload.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0].get("text", {}).get("body", "empty") 

    
    response = await chat(ChatRequest(phone=phone, message=message))
    await send_text(phone, response.get("response", "Désolé, une erreur est survenue."))     


def verify_signature(payload_bytes: bytes, signature: str) -> bool:
    if not WHATSAPP_TOKEN:
        return True
    expected = "sha256=" + hmac.new(
        key=WHATSAPP_TOKEN.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
async def send_text(to: str, text: str):
    """Send a text message via WhatsApp Business API."""
    if not WHATSAPP_TOKEN or not PHONE_ID:
        return
    url = f"{BASE_URL}/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text[:4096]},
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(url, json=payload, headers=headers)
        except Exception:
            pass



class ChatRequest(BaseModel):
    phone: str
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    """Endpoint de test Postman — retourne la réponse du bot directement en JSON (sans envoi WhatsApp)."""
    if not _session_mgr:
        return JSONResponse({"error": "Service not ready"}, status_code=503)

    phone = req.phone.strip()
    text  = req.message.strip()

    if not text:
        return JSONResponse({"error": "Le champ 'message' est vide"}, status_code=400)

    logger.info(f"[/chat] Message de {phone}: {text[:60]}")

    # Création du user s'il n'existe pas avec ce numéro
    await _safe(get_or_create_user(phone))

    # Récupération ou création de la session liée à l'user
    session = await _session_mgr.get(phone)
    if not session:
        session = await _session_mgr.create(phone, str(uuid.uuid4()))

    # Persist inbound message
    db_message_id = await _safe(save_message(session["session_id"], phone, text, "inbound"))

    # Intent
    intent_data = await _get_intent(text, session["session_id"])
    intent      = intent_data.get("intent", "UNKNOWN")
    print(f"Intent identifié: {intent}")
    # Persist intent classification result
    if db_message_id:
        await _safe(save_intent_message(db_message_id, intent))

    # Route
    result = await route_message(intent, text, session)

    # Update session state
    await _session_mgr.save(phone, session)

    # Persist outbound bot message
    response = result.get("message", "Je n'ai pas compris votre demande. Pouvez-vous reformuler ?")
    await _safe(save_message(session["session_id"], phone, response, "outbound"))

    return {"phone": phone, "response": response}


# ── Core processing ───────────────────────────────────────
async def _process(payload: dict):
    if not _session_mgr or not _wa:
        return

    msg = _wa.parse_incoming(payload)
    if not msg or not msg.get("text"):
        return

    phone      = msg["from"]
    text       = msg["text"].strip()
    message_id = msg["message_id"]

    logger.info(f"Message from {phone}: {text[:60]}")

    await _wa.mark_as_read(message_id)

    # Session
    session = await _session_mgr.get(phone)
    if not session:
        session = await _session_mgr.create(phone, str(uuid.uuid4()))

    # Persist inbound message
    db_message_id = await _safe(save_message(session["session_id"], phone, text, "inbound"))

    # Intent
    intent_data = await _get_intent(text)
    intent      = intent_data.get("intent", "UNKNOWN")
    print(f"Identified intent: {intent}")
    # Persist intent classification result
    if db_message_id:
        await _safe(save_intent_message(db_message_id, intent))

    # Route
    result = await route_message(intent, text, session)

    # Update session state
    await _session_mgr.save(phone, session)

    # Reply
    response = result.get("message", "Je n'ai pas compris votre demande. Pouvez-vous reformuler ?")

    # Persist outbound bot message
    await _safe(save_message(session["session_id"], phone, response, "outbound"))

    await _wa.send_text(phone, response)


async def _safe(coro):



    """Run a DB coroutine without letting errors break the main flow."""
    try:
        return await coro
    except Exception as exc:
        logger.error(f"DB persistence error: {exc}")
        return None


async def _get_intent(text: str, session_id: str = None) -> dict:
    try:
        contexte = None
        if session_id:
            from core.message_router import _get_recent_messages
            messages = await _get_recent_messages({"session_id": session_id}, limit=5)
            if messages and isinstance(messages, list) and len(messages) > 0:
                contexte = messages
                print(f"Contexte récupéré pour session {session_id}: {contexte}")

        payload = {"question": text}
        if contexte:
            payload["contexte"] = contexte

        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                f"{settings.intent_service_url}/rag/getIntent",
                json=payload,
            )
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict):
                    return data
                logger.warning(f"Intent service returned unexpected format: {data}")
            else:
                logger.warning(f"Intent service returned {r.status_code}")

    except Exception as e:
        logger.error(f"Intent service error: {e}")

    return {"intent": "UNKNOWN"}
