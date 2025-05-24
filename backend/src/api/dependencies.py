from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from src.db.database import SessionLocal
from src.utils.trace import generate_trace_header


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

def add_trace_header(
    response: Response,
) -> None:
    response.headers["server-timing"] = generate_trace_header()
