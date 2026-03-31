import uuid
from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    whatsapp_msg_id = Column(String(100), unique=True, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=True)
    direction = Column(String(10), nullable=False)  # INBOUND | OUTBOUND
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")
    intent_detected = Column(String(50), nullable=True)
    confidence = Column(Numeric(4, 3), nullable=True)

    user = relationship("User", back_populates="messages")
    session = relationship("Session", back_populates="messages")
    intent_log = relationship("IntentLog", back_populates="message", uselist=False)
    rag_query_log = relationship("RagQueryLog", back_populates="message", uselist=False)

    def __repr__(self):
        return f"<Message direction={self.direction} type={self.message_type}>"
