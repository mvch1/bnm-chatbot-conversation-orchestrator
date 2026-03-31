import uuid
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base


class IntentLog(Base):
    __tablename__ = "intent_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False)
    intent_name = Column(String(50), nullable=False)
    confidence = Column(Numeric(4, 3), nullable=False)
    entities = Column(JSONB, default=dict, nullable=False)
    latency_ms = Column(Integer, nullable=True)
    model_used = Column(String(50), default="gpt-4o")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    message = relationship("Message", back_populates="intent_log")

    def __repr__(self):
        return f"<IntentLog intent={self.intent_name} conf={self.confidence}>"
