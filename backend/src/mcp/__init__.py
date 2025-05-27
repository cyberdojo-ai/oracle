from mcp.server import FastMCP
from datetime import datetime, date, timedelta, time

from src.db import schemas, crud
from src.db.database import SessionLocal
from src.utils.embeddings import async_get_embedding

app = FastMCP()


@app.tool()
async def get_today_sources() -> list[schemas.Source]:
    """
        Retrieves a list of sources that have been published or updated today. This tool helps you quickly access all sources relevant to the current day. These sources may contain possible Indicators of Compromise (IOCs) useful for threat detection and response.
    """
    today = date.today()
    start_of_today = datetime.combine(today, time.min)
    end_of_today = datetime.combine(today, time.max)

    db = SessionLocal()
    try:
        sources = await crud.async_base_get_source(
            db=db,
            published_after=start_of_today,
            published_before=end_of_today + timedelta(seconds=1),
            order_by="published_on",
            asc=False,
        )
        updated_sources = await crud.async_base_get_source(
            db=db,
            updated_after=start_of_today,
            updated_before=end_of_today + timedelta(seconds=1),
            order_by="updated_on",
            asc=False,
        )
    finally:
        await db.close()

    all_sources = {s.id: s for s in sources}
    for s in updated_sources:
        all_sources[s.id] = s
    # Convert to schemas.Source
    return [schemas.Source.model_validate(s) for s in all_sources.values()]

@app.tool()
async def get_last_n_days_sources(
    last_n_days: int = 7
) -> list[schemas.Source]:
    """
        Retrieves a list of sources that have been published or updated within the last n days. This tool helps you quickly access all sources relevant to the current day. These sources may contain possible Indicators of Compromise (IOCs) useful for threat detection and response.
    """
    today = date.today()
    start_of_range = datetime.combine(today - timedelta(days=last_n_days - 1), time.min)
    end_of_today = datetime.combine(today, time.max)

    db = SessionLocal()
    try:
        published_sources = await crud.async_base_get_source(
            db=db,
            published_after=start_of_range,
            published_before=end_of_today + timedelta(seconds=1),
            order_by="published_on",
            asc=False,
        )
        updated_sources = await crud.async_base_get_source(
            db=db,
            updated_after=start_of_range,
            updated_before=end_of_today + timedelta(seconds=1),
            order_by="updated_on",
            asc=False,
        )
    finally:
        await db.close()

    all_sources = {s.id: s for s in published_sources}
    for s in updated_sources:
        all_sources[s.id] = s
    # Convert to schemas.Source
    return [schemas.Source.model_validate(s) for s in all_sources.values()]



@app.tool()
# async def search_sources() -> list[schemas.Source]:
async def search_sources(
    query: str,
    limit: int = 10
):
    """
        Searches for sources based on a query string. This tool helps you find sources that match specific keywords or phrases, which may contain possible Indicators of Compromise (IOCs) useful for threat detection and response.
    """
    db = SessionLocal()
    try:
        query_embedding = await async_get_embedding(query)

        sources = await crud.async_similarity_search_source_embedding(
            db=db,
            query_embedding=query_embedding,
            limit=limit*5,  # Retrieve more than the limit to handle deduplication
        )
    finally:
        await db.close()

    validated_sources: list[schemas.SourceWithDistance] = []
    for s in sources:
        model = schemas.Source.model_validate(s[0].source)
        model = schemas.SourceWithDistance(
            **model.model_dump(), distance=s[1]
        )
        validated_sources.append(model)
    
    # deduplicate sources by id with average distance
    unique_sources: dict[int, schemas.SourceWithDistance] = {}
    for source in validated_sources:
        if source.id not in unique_sources:
            unique_sources[source.id] = source
        else:
            existing_source = unique_sources[source.id]
            # Average the distances
            new_distance = (existing_source.distance + source.distance) / 2
            unique_sources[source.id] = schemas.SourceWithDistance(
                **existing_source.model_dump(exclude="distance"), distance=new_distance
            )
    # Convert to list
    validated_sources = list(unique_sources.values())
    # Apply the limit
    validated_sources = validated_sources[:limit]

    return validated_sources
