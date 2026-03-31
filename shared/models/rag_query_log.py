import uuid
from sqlalchemy import Column, Text, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base


class RagQueryLog(Base):
    __tablename__ = "rag_query_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False)
    query_text = Column(Text, nullable=False)
    retrieved_chunks = Column(JSONB, default=list, nullable=False)
    top_similarity = Column(Numeric(4, 3), nullable=True)
    generated_response = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    message = relationship("Message", back_populates="rag_query_log")

    def __repr__(self):
        return f"<RagQueryLog similarity={self.top_similarity} latency={self.latency_ms}ms>"
