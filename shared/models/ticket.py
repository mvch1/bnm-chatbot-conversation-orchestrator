import uuid
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=True)
    type = Column(String(50), nullable=False)  # COMPLAINT|WALLET_VALIDATION|ESCALATION
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="OPEN", nullable=False)
    priority = Column(String(10), default="NORMAL", nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    complaint = relationship("Complaint", back_populates="ticket")
    assigned_agent = relationship("Agent", back_populates="tickets", foreign_keys=[assigned_to])
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
    escalation = relationship("Escalation", back_populates="ticket", uselist=False)
    wallet_request = relationship("WalletValidationRequest", back_populates="ticket", uselist=False)

    def __repr__(self):
        return f"<Ticket type={self.type} status={self.status}>"
