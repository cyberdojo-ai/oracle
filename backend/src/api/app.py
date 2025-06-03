from fastapi import FastAPI, Depends
from warnings import warn


from src.config import config
from .dependencies import add_trace_header
from src.utils.trace import setup_tracing
from src.utils.metrics import setup_metrics


# Initialize tracing and metrics
config.application_name = config.application_name + " - API"

tracer = setup_tracing()
meter = setup_metrics()

app = FastAPI(
    title=config.application_name,
    description="Oracle API",
    dependencies=[Depends(add_trace_header)],
)

if config.enable_fastapi_telemetry:
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor().instrument_app(
            app,
            excluded_urls="/health",
        )
    except ImportError:
        warn("FastAPIInstrumentor not installed. Skipping FastAPI instrumentation.")

if config.enable_httpx_telemetry:
    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        HTTPXClientInstrumentor().instrument()
    except ImportError:
        warn("HTTPXClientInstrumentor not installed. Skipping HTTPX instrumentation.")


if config.environment == "development":
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )


@app.get(
    "/health",
    summary="Health check",
    description="Health check endpoint",
)
def health():
    return {"status": "ok"}

from .routers import api_router
app.include_router(
    api_router,
    prefix="/api",
    tags=["api"],
)
