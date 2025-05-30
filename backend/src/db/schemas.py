import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, Field, ConfigDict

from .models import JobStatus
from src.utils import current_utc_time


class EnrichmentJobBase(BaseModel):
    name: str
    description: str
    status: JobStatus = JobStatus.PENDING
    started_at: Optional[datetime.datetime | None] = None
    finished_at: Optional[datetime.datetime | None] = None

class EnrichmentJobCreate(EnrichmentJobBase):
    pass

class EnrichmentJobUpdate(BaseModel):
    status: Optional[JobStatus | None] = None
    started_at: Optional[datetime.datetime | None] = None
    finished_at: Optional[datetime.datetime | None] = None

class EnrichmentJob(EnrichmentJobBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class SourceBase(BaseModel):
    title: str
    type: str
    url: Optional[str] = None
    content: Optional[str] = None
    fetched_on: Optional[datetime.datetime | None] = None
    published_on: Optional[datetime.date | None] = None
    updated_on: Optional[datetime.datetime | None] = None
    enrichment_job_id: Optional[int | None] = None

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    content: Optional[str] = None
    fetched_on: Optional[datetime.datetime | None] = None
    published_on: Optional[datetime.date | None] = None
    updated_on: Optional[datetime.datetime | None] = None

class Source(SourceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class SourceEmbeddingBase(BaseModel):
    source_id: int
    chunk: str
    embedding: List[float]

class SourceEmbeddingCreate(SourceEmbeddingBase):
    pass
class SourceEmbeddingUpdate(BaseModel):
    chunk: Optional[str] = None
    embedding: Optional[List[float]] = None

class SourceEmbedding(SourceEmbeddingBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    source: Source

class SourceEmbeddingWithDistance(SourceEmbedding):
    distance: float

class SourceWithDistance(Source):
    distance: float

class IOCBase(BaseModel):
    value: str
    tags: Optional[List[str]] = Field(default_factory=list)
    source_id: Optional[int] = None

class IOCCreate(IOCBase):
    pass

class IOCUpdate(BaseModel):
    value: Optional[str] = None
    tags: Optional[List[str]] = None
    source_id: Optional[int] = None

class IOC(IOCBase):
    model_config = ConfigDict(from_attributes=True)
    id: int