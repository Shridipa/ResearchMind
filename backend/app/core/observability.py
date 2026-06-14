import logging

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from app.core.config import settings

logger = logging.getLogger(__name__)

def configure_observability(app: FastAPI):
    if not settings.enable_telemetry:
        return

    resource = Resource.create({"service.name": settings.app_name})
    tracer_provider = TracerProvider(resource=resource)
    
    # In a real environment, you'd export to OTLP (Jaeger, Datadog, AWS X-Ray, etc.)
    # For local development, we'll just log to console.
    # We could also use an OTLPSpanExporter if configured.
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    tracer_provider.add_span_processor(processor)
    
    trace.set_tracer_provider(tracer_provider)
    
    FastAPIInstrumentor.instrument_app(app)
    logger.info("OpenTelemetry observability configured")

