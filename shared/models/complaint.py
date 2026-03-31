import uuid
from sqlalchemy import Column, String, Text, Numeric, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number = Column(String(25), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=True)
    complaint_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Numeric(15, 2), nullable=True)
    transaction_date = Column(Date, nullable=True)
    reference_number = Column(String(100), nullable=True)
    status = Column(String(20), default="PENDING", nullable=False)
    priority = Column(String(10), default="NORMAL", nullable=False)
    assigned_agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    resolution_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="complaints")
    session = relationship("Session", back_populates="complaints")
    assigned_agent = relationship("Agent", back_populates="complaints", foreign_keys=[assigned_agent_id])
    ticket = relationship("Ticket", back_populates="complaint", uselist=False)

    def __repr__(self):
        return f"<Complaint {self.ticket_number} status={self.status}>"
