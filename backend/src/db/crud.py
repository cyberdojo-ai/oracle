from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, asc, desc
from pgvector.sqlalchemy import Vector
from datetime import datetime

from . import models, schemas

### Read operations ###

#### EnrichmentJob ####
async def async_base_get_enrichment_job(
    db: AsyncSession,
    id: int | None = None,
    name: str | None = None,
    description: str | None = None,
    status: str | None = None,
    offset: int = 0,
    limit: int = -1,
) -> list[models.EnrichmentJob]:

    stmt = select(models.EnrichmentJob)
    if id:
        stmt = stmt.filter(models.EnrichmentJob.id == id)
    if name:
        stmt = stmt.filter(models.EnrichmentJob.name == name)
    if description:
        stmt = stmt.filter(models.EnrichmentJob.description == description)
    if status:
        stmt = stmt.filter(models.EnrichmentJob.status == status)

    if limit > 0:
        stmt = stmt.limit(limit)

    stmt = stmt.offset(offset)

    res = await db.execute(stmt)
    return res.scalars().all()

#### Source ####
async def async_base_get_source(
    db: AsyncSession,
    id: int | None = None,
    enrichment_job_id: int | None = None,
    title: str | None = None,
    title_like: str | None = None,
    url: str | None = None,
    content_like: str | None = None,
    urls: list[str] | None = None,
    published_after: datetime | None = None,
    published_before: datetime | None = None,
    updated_after: datetime | None = None,  # NEW
    updated_before: datetime | None = None, # NEW
    order_by: str | None = None,
    asc: bool = False,
    offset: int = 0,
    limit: int = -1,
) -> list[models.Source]:

    stmt = select(models.Source)
    if id:
        stmt = stmt.filter(models.Source.id == id)
    if enrichment_job_id:
        stmt = stmt.filter(models.Source.enrichment_job_id == enrichment_job_id)
    if title:
        stmt = stmt.filter(models.Source.title == title)
    if title_like:
        stmt = stmt.filter(models.Source.title.ilike(f"%{title_like}%"))
    if url:
        stmt = stmt.filter(models.Source.url == url)
    if content_like:
        stmt = stmt.filter(models.Source.content.ilike(f"%{content_like}%"))
    if urls:
        stmt = stmt.filter(models.Source.url.in_(urls))

    if published_after:
        stmt = stmt.filter(models.Source.published_on > published_after)
    if published_before:
        stmt = stmt.filter(models.Source.published_on < published_before)
    if updated_after:
        stmt = stmt.filter(models.Source.updated_on > updated_after)
    if updated_before:
        stmt = stmt.filter(models.Source.updated_on < updated_before)

    if order_by:
        if asc:
            stmt = stmt.order_by(getattr(models.Source, order_by, "id").asc())
        else:
            stmt = stmt.order_by(getattr(models.Source, order_by, "id").desc())

    if limit > 0:
        stmt = stmt.limit(limit)

    stmt = stmt.offset(offset)

    res = await db.execute(stmt)
    return res.scalars().all()

### Source Embedding ###
async def async_similarity_search_source_embedding(
    db: AsyncSession,
    query_embedding: list[float],
    limit: int = 10,
) -> list[tuple[models.SourceEmbedding, float]]:
    """
    Perform a vector search on the source embeddings using cosine similarity.
    """
    stmt = select(
        models.SourceEmbedding,
        models.SourceEmbedding.embedding.cosine_distance(query_embedding).label("distance")
    )
    stmt = stmt.order_by(asc("distance"))
    if limit > 0:
        stmt = stmt.limit(limit)

    stmt = stmt.options(selectinload(models.SourceEmbedding.source))

    res = await db.execute(stmt)
    return res.all()
    

### Update operations ###

#### EnrichmentJob ####
async def async_base_update_enrichment_job(db: AsyncSession, enrichment_job: models.EnrichmentJob, enrichment_job_updated: schemas.EnrichmentJobUpdate) -> models.EnrichmentJob:
    # Check if at least one field is being updated
    json_update_dict = enrichment_job_updated.model_dump(exclude_none=True)
    if not json_update_dict:
        return None

    for field, value in json_update_dict.items():
        setattr(enrichment_job, field, value)
    db.add(enrichment_job)
    await db.commit()
    return enrichment_job

### Write operations ###

#### EnrichmentJob ####
async def async_base_create_enrichment_job(db: AsyncSession, enrichment_job: schemas.EnrichmentJobCreate) -> models.EnrichmentJob:
    db_enrichment_job = models.EnrichmentJob(**enrichment_job.model_dump())
    db.add(db_enrichment_job)
    await db.commit()
    return db_enrichment_job

#### Source ####
async def async_base_create_source(db: AsyncSession, source: schemas.SourceCreate) -> models.Source:
    db_source = models.Source(**source.model_dump())
    db.add(db_source)
    await db.commit()
    return db_source

### Source Embedding ###
async def async_base_create_source_embedding(
    db: AsyncSession, source_embedding: schemas.SourceEmbeddingCreate
) -> models.SourceEmbedding:
    db_source_embedding = models.SourceEmbedding(**source_embedding.model_dump())
    db.add(db_source_embedding)
    await db.commit()
    return db_source_embedding

### Read/Write operations ###

### Delete operations ###

async def async_count_sources(
    db: AsyncSession,
    id: int | None = None,
    enrichment_job_id: int | None = None,
    title: str | None = None,
    title_like: str | None = None,
    url: str | None = None,
    content_like: str | None = None,
    urls: list[str] | None = None,
    published_after: datetime | None = None,
    published_before: datetime | None = None,
) -> int:
    stmt = select(func.count()).select_from(models.Source)
    if id:
        stmt = stmt.filter(models.Source.id == id)
    if enrichment_job_id:
        stmt = stmt.filter(models.Source.enrichment_job_id == enrichment_job_id)
    if title:
        stmt = stmt.filter(models.Source.title == title)
    if title_like:
        stmt = stmt.filter(models.Source.title.ilike(f"%{title_like}%"))
    if url:
        stmt = stmt.filter(models.Source.url == url)
    if content_like:
        stmt = stmt.filter(models.Source.content.ilike(f"%{content_like}%"))
    if urls:
        stmt = stmt.filter(models.Source.url.in_(urls))
    if published_after:
        stmt = stmt.filter(models.Source.published_on > published_after)
    if published_before:
        stmt = stmt.filter(models.Source.published_on < published_before)
    res = await db.execute(stmt)
    return res.scalar() or 0
