from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Annotated, Literal
from datetime import datetime

from src.api.dependencies import get_db
from src.db import schemas, crud

router = APIRouter()


@router.get(
    "",
)
@router.get(
    "/",
)
async def get_source_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    content_like: str | None = Query(
        default=None,
        description="Filter sources by content",
    ),
    url: str | None = Query(
        default=None,
        description="Filter sources by URL",
    ),
    title_like: str | None = Query(
        default=None,
        description="Filter sources by title",
    ),
    published_after: datetime | None = Query(
        default=None,
        description="Filter sources published after this date",
    ),
    published_before: datetime | None = Query(
        default=None,
        description="Filter sources published before this date",
    ),
    order_by: Literal[
        "id",
        "title",
        "url",
        "content",
        "published_on",
        "updated_on",
        "fetched_on",
    ] = Query(
        default="published_on",
        description="Order by this field",
    ),
    asc: bool = Query(
        default=False,
        description="Order by ascending",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Offset for pagination",
    ),
    limit: int = Query(
        default=1_000,
        ge=1,
        le=1_000,
        description="Limit the number of sources returned",
    ),
) -> list[schemas.Source]:

    """
    Get sources from the database.
    """
    sources = await crud.async_base_get_source(
        db=db,
        content_like=content_like,
        title_like=title_like,
        url=url,
        published_after=published_after,
        published_before=published_before,
        order_by=order_by,
        asc=asc,
        offset=offset,
        limit=limit,
    )
    return sources


@router.get("/count")
async def count_sources_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    content_like: str | None = Query(default=None, description="Filter sources by content"),
    url: str | None = Query(default=None, description="Filter sources by URL"),
    title_like: str | None = Query(default=None, description="Filter sources by title"),
    published_after: datetime | None = Query(default=None, description="Filter sources published after this date"),
    published_before: datetime | None = Query(default=None, description="Filter sources published before this date"),
) -> dict:
    count = await crud.async_count_sources(
        db=db,
        content_like=content_like,
        title_like=title_like,
        url=url,
        published_after=published_after,
        published_before=published_before,
    )
    return {"count": count}
