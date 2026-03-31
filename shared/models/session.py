import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Session(Base, TimestampMixin):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    state = Column(String(50), nullable=False, default="GREETING")
    collected_data = Column(JSONB, default={})
    intent_history = Column(JSONB, default=[])
    ended_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")
    workflow_steps = relationship("WorkflowStepLog", back_populates="session")
    escalations = relationship("Escalation", back_populates="session")

    def __repr__(self):
        return f"<Session id={self.id} state={self.state}>"
