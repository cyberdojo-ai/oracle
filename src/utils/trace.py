from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, DEPLOYMENT_ENVIRONMENT
import os

from src.config import config
from src.utils import run_once


@run_once
def setup_tracing() -> trace.Tracer:
    # Create a resource with the service name attribute.
    resource = Resource.create(
        attributes={
            SERVICE_NAME: config.application_name,
            DEPLOYMENT_ENVIRONMENT: config.environment,
        }
    )
    # Initialize the TracerProvider with the created resource.
    trace.set_tracer_provider(TracerProvider(resource=resource))


    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        span_exporter = OTLPSpanExporter()

        span_processor = BatchSpanProcessor(span_exporter) if config.tracing_batch_processor else SimpleSpanProcessor(span_exporter)
    else:
        span_exporter = ConsoleSpanExporter()
        span_processor = SimpleSpanProcessor(span_exporter)

    tp = trace.get_tracer_provider()
    tp.add_span_processor(span_processor)

    return trace.get_tracer(__name__)

def generate_trace_header() -> str:
    span = trace.get_current_span()
    if span.is_recording():
        trace_id = span.get_span_context().trace_id
        span_id = span.get_span_context().span_id
        return f'traceparent;desc="00-{trace_id}-{span_id}-01"'
    return ""
