import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="AGENT", nullable=False)  # AGENT|SUPERVISOR|ADMIN
    status = Column(String(20), default="AVAILABLE")  # AVAILABLE|BUSY|OFFLINE
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    complaints = relationship("Complaint", back_populates="assigned_agent", foreign_keys="Complaint.assigned_agent_id")
    tickets = relationship("Ticket", back_populates="assigned_agent", foreign_keys="Ticket.assigned_to")
    comments = relationship("TicketComment", back_populates="agent")
    escalations = relationship("Escalation", back_populates="assigned_agent")
    wallet_reviews = relationship("WalletValidationRequest", back_populates="reviewer")

    def __repr__(self):
        return f"<Agent email={self.email} role={self.role}>"
