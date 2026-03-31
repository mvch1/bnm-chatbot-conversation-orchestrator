import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class WalletValidationRequest(Base):
    __tablename__ = "wallet_validation_requests"
    __table_args__ = (UniqueConstraint("session_id", name="uq_wallet_session"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=True)
    phone_number = Column(String(20), nullable=False)
    cin_number = Column(String(20), nullable=True)
    document_path = Column(String(500), nullable=True)
    document_type = Column(String(20), default="CIN")
    status = Column(String(20), default="PENDING", nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    attempt_number = Column(Integer, default=1, nullable=False)

    user = relationship("User", back_populates="wallet_requests")
    session = relationship("Session", back_populates="wallet_requests")
    ticket = relationship("Ticket", back_populates="wallet_request")
    reviewer = relationship("Agent", back_populates="wallet_reviews")

    def __repr__(self):
        return f"<WalletValidationRequest status={self.status} attempt={self.attempt_number}>"
