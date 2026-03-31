"""
Database repository — centralised persistence helpers.

All services import from here to keep DB logic in one place.
Each function is self-contained: it opens its own session via get_db().
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from database.models import User, Session, Message, Intent, IntentMessage, Agent, Ticket
from shared.utils.logger import get_logger

logger = get_logger("database.repository")


# ── Session (PostgreSQL-backed) ───────────────────────────────────────────────

def _session_to_dict(db_session: Session) -> Dict[str, Any]:
    """Convert a Session ORM object to the dict format used by SessionManager."""
    return {
        "session_id": db_session.id,
        "user_phone": db_session.user.phone if db_session.user else None,
        "state": db_session.state,
        "collected_data": db_session.collected_data or {},
        "step_index": db_session.step_index or 0,
        "created_at": db_session.created_at.isoformat(),
        "updated_at": db_session.updated_at.isoformat(),
    }


async def get_session_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """Return the most recent open Session for a phone number, or None."""
    async with get_db() as db:
        result = await db.execute(
            select(Session)
            .join(User, Session.user_id == User.id)
            .where(User.phone == phone, Session.closed_at.is_(None))
            .order_by(Session.created_at.desc())
        )
        db_session = result.scalars().first()
        if db_session is None:
            return None
        # Eagerly load user relation for phone access
        await db.refresh(db_session, ["user"])
        return _session_to_dict(db_session)


async def create_session(phone: str, session_id: str) -> Dict[str, Any]:
    """Create a new Session linked to the user and return its dict."""
    user = await get_or_create_user(phone)
    async with get_db() as db:
        db_session = Session(
            id=session_id,
            user_id=user.id,
            state="GREETING",
            collected_data={},
            step_index=0,
        )
        db.add(db_session)
        await db.flush()
        await db.refresh(db_session)
        logger.info(f"Created session id={session_id} for phone={phone}")
        return {
            "session_id": db_session.id,
            "user_phone": phone,
            "state": db_session.state,
            "collected_data": db_session.collected_data,
            "step_index": db_session.step_index,
            "created_at": db_session.created_at.isoformat(),
            "updated_at": db_session.updated_at.isoformat(),
        }


async def update_session(phone: str, session_data: Dict[str, Any]) -> None:
    """Persist session dict changes back to the DB row."""
    async with get_db() as db:
        result = await db.execute(
            select(Session)
            .join(User, Session.user_id == User.id)
            .where(User.phone == phone, Session.closed_at.is_(None))
            .order_by(Session.created_at.desc())
        )
        db_session = result.scalars().first()
        if db_session is None:
            logger.warning(f"update_session: no open session found for phone={phone}")
            return
        db_session.state = session_data.get("state", db_session.state)
        db_session.collected_data = session_data.get("collected_data", db_session.collected_data)
        db_session.step_index = session_data.get("step_index", db_session.step_index)
        db_session.updated_at = datetime.now(timezone.utc)


async def delete_session(phone: str) -> None:
    """Close (soft-delete) the most recent open session for a phone number."""
    async with get_db() as db:
        result = await db.execute(
            select(Session)
            .join(User, Session.user_id == User.id)
            .where(User.phone == phone, Session.closed_at.is_(None))
            .order_by(Session.created_at.desc())
        )
        db_session = result.scalars().first()
        if db_session:
            db_session.closed_at = datetime.now(timezone.utc)
            logger.info(f"Closed session id={db_session.id} for phone={phone}")



async def get_or_create_user(phone: str) -> User:
    """Return existing User or create a new one."""
    async with get_db() as db:
        result = await db.execute(select(User).where(User.phone == phone))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(phone=phone)
            db.add(user)
            await db.flush()
            logger.info(f"Created user phone={phone}")
        return user


async def get_or_create_db_session(session_id: str, phone: str) -> Session:
    """Return existing DB Session or create a new one linked to the user."""
    async with get_db() as db:
        result = await db.execute(select(Session).where(Session.id == session_id))
        db_session = result.scalar_one_or_none()
        if db_session is None:
            # Ensure user exists first (separate transaction)
            user = await get_or_create_user(phone)
            db_session = Session(id=session_id, user_id=user.id)
            db.add(db_session)
            await db.flush()
            logger.info(f"Created DB session id={session_id}")
        return db_session


# ── Message ───────────────────────────────────────────────────────────────────

async def save_message(
    session_id: str,
    phone: str,
    content: str,
    direction: str = "inbound",
) -> str:
    """Persist a Message and return its ID."""
    # Ensure the DB session row exists
    await get_or_create_db_session(session_id, phone)

    async with get_db() as db:
        msg = Message(
            session_id=session_id,
            direction=direction,
            content=content,
        )
        db.add(msg)
        await db.flush()
        message_id = msg.id
        logger.info(f"Saved message id={message_id} direction={direction}")
        return message_id


# ── IntentMessage ─────────────────────────────────────────────────────────────

async def save_intent_message(message_id: str, raw_intent: str) -> None:
    """Create an IntentMessage linked to a Message. Resolves Intent FK if code exists."""
    async with get_db() as db:
        # Try to resolve Intent catalogue entry
        result = await db.execute(select(Intent).where(Intent.code == raw_intent))
        intent = result.scalar_one_or_none()

        im = IntentMessage(
            message_id=message_id,
            intent_id=intent.id if intent else None,
            raw_intent=raw_intent,
        )
        db.add(im)
        logger.info(f"Saved IntentMessage message_id={message_id} intent={raw_intent}")


# ── Agent ─────────────────────────────────────────────────────────────────────

async def get_available_agent() -> Optional[Agent]:
    """Return the first active agent (round-robin assignment can be added later)."""
    async with get_db() as db:
        result = await db.execute(
            select(Agent).where(Agent.is_active == True).limit(1)  # noqa: E712
        )
        return result.scalar_one_or_none()


# ── Ticket ────────────────────────────────────────────────────────────────────

async def save_ticket(
    session_id: str,
    phone: str,
    ticket_number: str,
    description: Optional[str] = None,
) -> Ticket:
    """Create a Ticket linked to the Session and an available Agent."""
    # Ensure session row exists
    await get_or_create_db_session(session_id, phone)

    agent = await get_available_agent()
    if agent is None:
        logger.warning("No available agent found — ticket created without agent assignment")

    async with get_db() as db:
        ticket = Ticket(
            number=ticket_number,
            session_id=session_id,
            agent_id=agent.id if agent else None,
            status="open",
            description=description,
        )
        db.add(ticket)
        await db.flush()
        logger.info(
            f"Saved ticket number={ticket_number} session={session_id} "
            f"agent={agent.name if agent else 'unassigned'}"
        )
        return ticket
