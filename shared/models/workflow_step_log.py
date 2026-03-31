import uuid
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class WorkflowStepLog(Base):
    __tablename__ = "workflow_step_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    workflow_type = Column(String(50), nullable=False)  # COMPLAINT|WALLET_VALIDATION
    step_index = Column(Integer, nullable=False)
    step_name = Column(String(50), nullable=False)
    user_input = Column(Text, nullable=True)
    bot_response = Column(Text, nullable=True)
    is_valid = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("Session", back_populates="workflow_steps")
    escalation = relationship("Escalation", back_populates="last_step", uselist=False)

    def __repr__(self):
        return f"<WorkflowStepLog step={self.step_index} name={self.step_name} valid={self.is_valid}>"
