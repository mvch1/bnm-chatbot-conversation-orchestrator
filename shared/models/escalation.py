import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=True)
    last_step_id = Column(UUID(as_uuid=True), ForeignKey("workflow_step_logs.id"), nullable=True)
    reason = Column(String(50), nullable=False)
    confidence_at_escalation = Column(Numeric(4, 3), nullable=True)
    status = Column(String(20), default="PENDING", nullable=False)
    assigned_agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_at = Column(DateTime(timezone=True), nullable=True)

    session = relationship("Session", back_populates="escalations")
    ticket = relationship("Ticket", back_populates="escalation")
    last_step = relationship("WorkflowStepLog", back_populates="escalation")
    assigned_agent = relationship("Agent", back_populates="escalations")

    def __repr__(self):
        return f"<Escalation reason={self.reason} status={self.status}>"
