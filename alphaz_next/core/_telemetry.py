# MODULES
import os as _os
import logging as _logging
from typing import Optional as _Optional

# FASTAPI
from fastapi import FastAPI as _FastAPI

# OPENTELEMETRY
from opentelemetry import metrics, trace, _logs
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# MODELS
from alphaz_next.models.config.alpha_config import (
    AlphaConfigSchema as _AlphaConfigSchema,
)


def _setup_traces(
    default_endpoint: str,
    default_headers: _Optional[str] = None,
    certificate_file: _Optional[str] = None,
    resource: _Optional[Resource] = None,
) -> None:
    """
    Set up traces for telemetry.

    Args:
        default_endpoint (str): The default endpoint for exporting traces.
        default_headers (str, optional): The default headers for exporting traces. Defaults to None.
        certificate_file (str, optional): The certificate file for exporting traces. Defaults to None.
        resource (Resource, optional): The resource for exporting traces. Defaults to None.
    """

    endpoint = _os.environ.get(
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
        f"{default_endpoint}/v1/traces",
    )

    headers = _os.environ.get(
        "OTEL_EXPORTER_OTLP_TRACES_HEADERS",
        default_headers,
    )

    exporter = OTLPSpanExporter(
        endpoint=endpoint,
        certificate_file=certificate_file,
        headers=headers,
    )

    processor = BatchSpanProcessor(exporter)
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(processor)


def _setup_metrics(
    default_endpoint: str,
    default_headers: _Optional[str] = None,
    certificate_file: _Optional[str] = None,
    resource: _Optional[Resource] = None,
):
    """
    Set up metrics configuration for telemetry.

    Args:
        default_endpoint (str): The default endpoint for exporting metrics.
        default_headers (str, optional): The default headers for exporting metrics. Defaults to None.
        certificate_file (str, optional): The path to the certificate file. Defaults to None.
        resource (Resource, optional): The resource associated with the metrics. Defaults to None.
    """

    endpoint = _os.environ.get(
        "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
        f"{default_endpoint}/v1/metrics",
    )

    headers = _os.environ.get(
        "OTEL_EXPORTER_OTLP_METRICS_HEADERS",
        default_headers,
    )

    exporter = OTLPMetricExporter(
        endpoint=endpoint,
        certificate_file=certificate_file,
        headers=headers,
    )
    reader = PeriodicExportingMetricReader(exporter=exporter)
    provider = MeterProvider(
        resource=resource,
        metric_readers=[reader],
    )
    metrics.set_meter_provider(provider)


def _setup_logs(
    default_endpoint: str,
    default_headers: _Optional[str] = None,
    certificate_file: _Optional[str] = None,
    resource: _Optional[Resource] = None,
) -> LoggingHandler:
    """
    Set up logs for telemetry.

    Args:
        default_endpoint (str): The default endpoint for exporting logs.
        default_headers (str, optional): The default headers for exporting logs. Defaults to None.
        certificate_file (str, optional): The path to the certificate file. Defaults to None.
        resource (Resource, optional): The resource associated with the logs. Defaults to None.

    Returns:
        LoggingHandler: The logging handler for the telemetry logs.
    """

    endpoint = _os.environ.get(
        "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT",
        f"{default_endpoint}/v1/logs",
    )

    headers = _os.environ.get(
        "OTEL_EXPORTER_OTLP_LOGS_HEADERS",
        default_headers,
    )

    exporter = OTLPLogExporter(
        endpoint=endpoint,
        certificate_file=certificate_file,
        headers=headers,
    )
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    _logs.set_logger_provider(logger_provider)

    return LoggingHandler(level=_logging.INFO, logger_provider=logger_provider)


def setup_telemetry(config: _AlphaConfigSchema, app: _FastAPI):
    """
    Sets up OpenTelemetry for the application.

    Args:
        config (_AlphaConfigSchema): The configuration object.
        app (_FastAPI): The FastAPI application object.

    Returns:
        None
    """

    if config.api_config.apm is None or not config.api_config.apm.active:
        return None

    otel_service_name = config.project_name
    apm_server_url = config.api_config.apm.server_url
    certificate_path = config.api_config.apm.certificate_file
    environment = config.environment.lower()
    version = config.version

    otel_exporter_otlp_headers = _os.environ.get(
        "OTEL_EXPORTER_OTLP_HEADERS",
        None,
    )

    otel_exporter_otlp_endpoint = _os.environ.get(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        apm_server_url,
    )

    otel_exporter_otl_certificate = _os.environ.get(
        "OTEL_EXPORTER_OTLP_CERTIFICATE",
        certificate_path,
    )

    resource_attributes = (
        _os.environ.get("OTEL_RESOURCE_ATTRIBUTES")
        or f"service.version={version},deployment.environment={environment}"
    )
    key_value_pairs = resource_attributes.split(",")
    result_dict = {}

    for pair in key_value_pairs:
        key, value = pair.split("=")
        result_dict[key] = value

    resourceAttributes = {
        "service.name": otel_service_name,
        "service.version": result_dict["service.version"],
        "deployment.environment": result_dict["deployment.environment"],
    }

    resource = Resource.create(resourceAttributes)

    _setup_traces(
        default_endpoint=otel_exporter_otlp_endpoint,
        certificate_file=otel_exporter_otl_certificate,
        default_headers=otel_exporter_otlp_headers,
        resource=resource,
    )

    _setup_metrics(
        default_endpoint=otel_exporter_otlp_endpoint,
        certificate_file=otel_exporter_otl_certificate,
        default_headers=otel_exporter_otlp_headers,
        resource=resource,
    )

    telemetry_handler = _setup_logs(
        default_endpoint=otel_exporter_otlp_endpoint,
        certificate_file=otel_exporter_otl_certificate,
        default_headers=otel_exporter_otlp_headers,
        resource=resource,
    )

    app.extra["telemetry_handler"] = telemetry_handler

    FastAPIInstrumentor().instrument_app(app)
