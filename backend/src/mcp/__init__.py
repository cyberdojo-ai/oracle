from warnings import warn
from mcp.server import FastMCP
from opentelemetry import trace
from datetime import datetime, date, timedelta, time
import json

from src.config import config
from src.db import schemas, crud
from src.db.database import SessionLocal
from src.utils.embeddings import async_get_embedding
from src.utils.trace import setup_tracing
from src.utils.metrics import setup_metrics


# Initialize tracing and metrics
config.application_name = config.application_name + " - MCP"

tracer = setup_tracing()
meter = setup_metrics()

app = FastMCP()


@app.tool()
async def get_today_sources() -> str:
    """
        Retrieves a list of sources that have been published or updated today. This tool helps you quickly access all sources relevant to the current day. These sources may contain possible Indicators of Compromise (IOCs) useful for threat detection and response.
    """
    with tracer.start_as_current_span("get_today_sources") as span:
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
        return json.dumps([schemas.Source.model_validate(s) for s in all_sources.values()])

@app.tool()
async def get_last_n_days_sources(
    last_n_days: int = 7
) -> str:

    """
        Retrieves a list of sources that have been published or updated within the last n days. This tool helps you quickly access all sources relevant to the current day. These sources may contain possible Indicators of Compromise (IOCs) useful for threat detection and response.
    """
    with tracer.start_as_current_span("get_last_n_days_sources") as span:
        span.set_attribute("last_n_days", last_n_days)
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
        return json.dumps([schemas.Source.model_validate(s) for s in all_sources.values()])



@app.tool()
async def search_sources(
    query: str,
    limit: int = 10
) -> str:
    """
        Performs a similarity search on the source embeddings to find relevant sources based on a query string. This tool helps you find sources that are similiar to the query, which may contain possible Indicators of Compromise (IOCs) useful for threat detection and response.
    """
    with tracer.start_as_current_span("search_sources") as span:
        span.set_attribute("query", query)
        span.set_attribute("limit", limit)
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

        # deduplicate sources by id and compute average distance correctly
        distance_accumulator: dict[int, tuple[schemas.SourceWithDistance, float, int]] = {}
        for source in validated_sources:
            if source.id not in distance_accumulator:
                distance_accumulator[source.id] = (source, source.distance, 1)
            else:
                existing_source, total_distance, count = distance_accumulator[source.id]
                distance_accumulator[source.id] = (existing_source, total_distance + source.distance, count + 1)

        # Compute average distance for each unique source
        unique_sources: list[schemas.SourceWithDistance] = []
        for source_id, (source, total_distance, count) in distance_accumulator.items():
            avg_distance = total_distance / count
            unique_sources.append(schemas.SourceWithDistance(
                **source.model_dump(exclude="distance"), distance=avg_distance
            ))
        # Sort by distance
        unique_sources.sort(key=lambda x: x.distance)
        # Apply the limit
        validated_sources = unique_sources[:limit]

        return json.dumps(validated_sources)
