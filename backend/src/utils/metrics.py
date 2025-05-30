from opentelemetry import metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, DEPLOYMENT_ENVIRONMENT
import os

from src.config import config
from src.utils import run_once


@run_once
def setup_metrics() -> metrics.Meter:
    # Create a resource with the service name attribute.
    resource = Resource.create(
        attributes={
            SERVICE_NAME: config.application_name,
            DEPLOYMENT_ENVIRONMENT: config.environment,
        }
    )

    # Configure the span exporter and processor based on whether the endpoint is effectively set.
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        metric_exporter = OTLPMetricExporter()
    else:
        metric_exporter = ConsoleMetricExporter()

    metric_reader = PeriodicExportingMetricReader(metric_exporter)

    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])

    metrics.set_meter_provider(meter_provider)

    return metrics.get_meter(__name__)
