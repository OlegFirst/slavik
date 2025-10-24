"""
Distributed Tracing with OpenTelemetry
Trace requests across all services
"""

import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.sdk.resources import Resource

logger = logging.getLogger(__name__)


def setup_tracing(service_name: str, jaeger_endpoint: str = "http://localhost:14268/api/traces"):
    """Setup OpenTelemetry tracing"""

    # Create resource
    resource = Resource(attributes={
        "service.name": service_name,
        "service.version": "2.0.0"
    })

    # Create tracer provider
    trace.set_tracer_provider(TracerProvider(resource=resource))

    # Create Jaeger exporter
    jaeger_exporter = JaegerExporter(
        collector_endpoint=jaeger_endpoint
    )

    # Add span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    logger.info(f"Distributed tracing initialized for {service_name}")


def instrument_fastapi(app):
    """Instrument FastAPI application"""
    FastAPIInstrumentor.instrument_app(app)
    logger.info("FastAPI instrumented for tracing")


def instrument_redis():
    """Instrument Redis"""
    RedisInstrumentor().instrument()
    logger.info("Redis instrumented for tracing")


def instrument_postgresql():
    """Instrument PostgreSQL"""
    AsyncPGInstrumentor().instrument()
    logger.info("PostgreSQL instrumented for tracing")


# Usage in service:
# from infrastructure.observability.tracing import setup_tracing, instrument_fastapi
# setup_tracing("my-service")
# instrument_fastapi(app)
