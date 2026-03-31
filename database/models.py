"""
Database models for the banking chatbot platform.

Entities:
    User          — registered user (customer)
    Session       — conversation session linked to a User
    Message       — individual message within a Session
    Intent        — intent catalogue (reference table)
    IntentMessage — classification result for a Message
    Agent         — human agent who can handle escalations
    Ticket        — support ticket linked to a Session and an Agent
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, Integer, Float,
    Boolean, DateTime, ForeignKey, Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


# ── User ──────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id         = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    phone      = Column(String(20), unique=True, nullable=False, index=True)
    name       = Column(String(120), nullable=True)
    is_active  = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    # One User → many Sessions
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User phone={self.phone}>"


# ── Session ───────────────────────────────────────────────────────────────────

class Session(Base):
    __tablename__ = "sessions"

    id             = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    user_id        = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    state          = Column(String(50), default="GREETING", nullable=False)
    collected_data = Column(JSONB, default=dict, nullable=False)
    step_index     = Column(Integer, default=0, nullable=False)
    created_at     = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at     = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)
    closed_at      = Column(DateTime(timezone=True), nullable=True)

    # Relations
    user     = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    tickets  = relationship("Ticket", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session id={self.id} state={self.state}>"


# ── Message ───────────────────────────────────────────────────────────────────

class Message(Base):
    __tablename__ = "messages"

    id         = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    session_id = Column(UUID(as_uuid=False), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    direction  = Column(SAEnum("inbound", "outbound", name="message_direction"), nullable=False)
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # Relations
    session        = relationship("Session", back_populates="messages")
    intent_message = relationship("IntentMessage", back_populates="message", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Message id={self.id} direction={self.direction}>"


# ── Intent ────────────────────────────────────────────────────────────────────

class Intent(Base):
    """Reference catalogue of known intents."""
    __tablename__ = "intents"

    id          = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    code        = Column(String(60), unique=True, nullable=False, index=True)
    label       = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)

    # Relations
    intent_messages = relationship("IntentMessage", back_populates="intent")

    def __repr__(self):
        return f"<Intent code={self.code}>"


# ── IntentMessage ─────────────────────────────────────────────────────────────

class IntentMessage(Base):
    """Classification result attached to a Message."""
    __tablename__ = "intent_messages"

    id         = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    message_id = Column(UUID(as_uuid=False), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    intent_id  = Column(UUID(as_uuid=False), ForeignKey("intents.id", ondelete="SET NULL"), nullable=True, index=True)
    raw_intent = Column(String(60), nullable=False)   # raw string returned by the intent service
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # Relations
    message = relationship("Message", back_populates="intent_message")
    intent  = relationship("Intent", back_populates="intent_messages")

    def __repr__(self):
        return f"<IntentMessage raw={self.raw_intent}>"


# ── Agent ─────────────────────────────────────────────────────────────────────

class Agent(Base):
    __tablename__ = "agents"

    id         = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    name       = Column(String(120), nullable=False)
    email      = Column(String(180), unique=True, nullable=False, index=True)
    is_active  = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    # Relations
    tickets = relationship("Ticket", back_populates="agent")

    def __repr__(self):
        return f"<Agent name={self.name}>"


# ── Ticket ────────────────────────────────────────────────────────────────────

class Ticket(Base):
    __tablename__ = "tickets"

    id            = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    number        = Column(String(20), unique=True, nullable=False, index=True)  # e.g. REC-A1B2C3D4
    session_id    = Column(UUID(as_uuid=False), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id      = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    status        = Column(SAEnum("open", "in_progress", "resolved", "closed", name="ticket_status"), default="open", nullable=False)
    description   = Column(Text, nullable=True)
    created_at    = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at    = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)
    resolved_at   = Column(DateTime(timezone=True), nullable=True)

    # Relations
    session = relationship("Session", back_populates="tickets")
    agent   = relationship("Agent", back_populates="tickets")

    def __repr__(self):
        return f"<Ticket number={self.number} status={self.status}>"
