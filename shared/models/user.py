import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    account_ref = Column(String(50), nullable=True)
    language = Column(String(10), default="fr")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    is_blocked = Column(Boolean, default=False)

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user")
    complaints = relationship("Complaint", back_populates="user")
    wallet_requests = relationship("WalletValidationRequest", back_populates="user")

    def __repr__(self):
        return f"<User phone={self.phone_number} name={self.name}>"
