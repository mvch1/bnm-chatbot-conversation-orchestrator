import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class DocumentSource(Base):
    __tablename__ = "document_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), unique=True, nullable=False)
    title = Column(String(200), nullable=True)
    category = Column(String(50), default="GENERAL")
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    md5_hash = Column(String(32), nullable=True)
    chunk_count = Column(Integer, default=0)
    ingested_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    chunks = relationship("DocumentChunk", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DocumentSource filename={self.filename} chunks={self.chunk_count}>"
