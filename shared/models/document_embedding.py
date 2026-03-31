import uuid
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

# Try to import pgvector, fallback to Text for environments without it
try:
    from pgvector.sqlalchemy import Vector
    VECTOR_COLUMN = Column(Vector(1536), nullable=False)
except ImportError:
    VECTOR_COLUMN = Column(Text, nullable=False)  # fallback


class DocumentEmbedding(Base, TimestampMixin):
    __tablename__ = "document_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(
        UUID(as_uuid=True),
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    model_name = Column(String(50), default="text-embedding-3-small")

    chunk = relationship("DocumentChunk", back_populates="embedding")

    def __repr__(self):
        return f"<DocumentEmbedding model={self.model_name}>"

    # Define embedding column separately to handle the pgvector import
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)


# Add embedding column after class definition
try:
    from pgvector.sqlalchemy import Vector
    DocumentEmbedding.embedding = Column(Vector(1536), nullable=False)
except ImportError:
    DocumentEmbedding.embedding = Column(Text, nullable=False)
