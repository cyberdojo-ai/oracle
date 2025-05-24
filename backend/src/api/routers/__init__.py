from fastapi import APIRouter
from .source import router as source_router

api_router = APIRouter()

api_router.include_router(
    source_router,
    prefix="/source",
    tags=["source"],
)
