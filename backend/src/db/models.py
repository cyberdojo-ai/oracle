import enum
from sqlalchemy import Column, ForeignKey, Integer, String, Enum, DateTime, Text, Date, Index
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship

from .database import Base


class JobStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class IOC(Base):
    __tablename__ = "iocs"

    id = Column(Integer, primary_key=True, index=True)

    source_id = Column(Integer, ForeignKey("sources.id"))

    value = Column(String, unique=True, nullable=False, index=True)

    tags = Column(ARRAY(String), default=[])

    source = relationship("Source", back_populates="iocs")

class SourceEmbedding(Base):
    __tablename__ = "source_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)

    chunk = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    
    source = relationship("Source")

Index(
    "sources_embedding_idx",
    SourceEmbedding.embedding,
    postgresql_using="hnsw",
    postgresql_ops={"embedding": "public.vector_cosine_ops"},
    postgresql_with={"m": "16", "ef_construction": "200"}
)

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    enrichment_job_id = Column(Integer, ForeignKey("enrichment_jobs.id"))

    type = Column(String, nullable=False, index=True)

    title = Column(String, nullable=False)
    url = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)

    fetched_on = Column(DateTime(timezone=True), nullable=True)
    published_on = Column(Date, nullable=True)
    updated_on = Column(DateTime(timezone=True), nullable=True)

    iocs = relationship("IOC", back_populates="source")
    enrichment_job = relationship("EnrichmentJob", back_populates="sources")

class EnrichmentJob(Base):
    __tablename__ = "enrichment_jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(JobStatus), nullable=False)  # Now using Enum

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    sources = relationship("Source", back_populates="enrichment_job")

