# MODULES
import os as _os
import logging as _logging
import platform as _platform
import psutil as _psutil
from typing import (
    Any as _Any,
    Dict as _Dict,
    Generator as _Generator,
    Optional as _Optional,
    List as _List,
    Tuple as _Tuple,
    NamedTuple as _NamedTuple,
    cast,
)

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
from opentelemetry.sdk.resources import (
    Attributes,
    Resource,
    SERVICE_NAME,
    SERVICE_VERSION,
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_INSTANCE_ID,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.system_metrics import (
    SystemMetricsInstrumentor as _SystemMetricsInstrumentor,
)
from opentelemetry.metrics import (
    Meter,
    CallbackOptions,
    Observation,
)

# MODELS
from alphaz_next.models.config.alpha_config import (
    AlphaConfigSchema as _AlphaConfigSchema,
)


class MemoryInfo(_NamedTuple):
    vms: int
    rss: int


class SystemMetricsInstrumentor(_SystemMetricsInstrumentor):

    def __init__(
        self,
        labels: _Dict[str, str] | None = None,
        config: _Dict[str, _Optional[_List[str]]] | None = None,
    ):
        super().__init__(labels, cast(_Dict[str, _List[str]], config))

        self._process = _psutil.Process()
        self._process.cpu_percent(interval=None)

        self._system_cpu_total_norm_pct_labels = self._labels.copy()
        self._system_memory_actual_free_labels = self._labels.copy()
        self._system_memory_total_labels = self._labels.copy()
        self._system_process_cpu_total_norm_pct_labels = self._labels.copy()
        self._system_process_memory_size_labels = self._labels.copy()
        self._system_process_memory_rss_byte_labels = self._labels.copy()

    def _instrument(self, **kwargs: _Any) -> None:
        super()._instrument(**kwargs) # type: ignore

        meter = cast(Meter, self._meter)

        if "system.cpu.total.norm.pct" in self._config:
            meter.create_observable_gauge(
                name="system.cpu.total.norm.pct",
                callbacks=[self._get_system_cpu_total_norm_pct],
                description="System CPU total normalized percent",
            )

        if "system.memory.actual.free" in self._config:
            meter.create_observable_gauge(
                name="system.memory.actual.free",
                callbacks=[self._get_system_memory_actual_free],
                description="System memory actual free",
            )

        if "system.memory.total" in self._config:
            meter.create_observable_gauge(
                name="system.memory.total",
                callbacks=[self._get_system_memory_total],
                description="System memory total",
            )

        if "system.process.cpu.total.norm.pct" in self._config:
            meter.create_observable_gauge(
                name="system.process.cpu.total.norm.pct",
                callbacks=[self._get_system_process_cpu_total_norm_pct],
                description="System process CPU total normalized percent",
            )

        if "system.process.memory.size" in self._config:
            meter.create_observable_gauge(
                name="system.process.memory.size",
                callbacks=[self._get_system_process_memory_size],
                description="System process memory size",
            )

        if "system.process.memory.rss.byte" in self._config:
            meter.create_observable_gauge(
                name="system.process.memory.rss.bytes",
                callbacks=[self._get_system_process_memory_rss_byte],
                description="System process memory rss bytes",
            )

    def _get_process_infos(self, p: _psutil.Process) -> _Tuple[float, MemoryInfo]:
        if hasattr(p, "oneshot"):  # new in psutil 5.0
            with p.oneshot():
                cpu_percent = p.cpu_percent(interval=None)
                memory_info = p.memory_info()
        else:
            cpu_percent = p.cpu_percent(interval=None)
            memory_info = p.memory_info()

        return cpu_percent, cast(MemoryInfo, memory_info)

    def _get_system_cpu_total_norm_pct(
        self,
        options: CallbackOptions,
    ) -> _Generator[Observation, None, None]:
        cpu_norm_percent = _psutil.cpu_percent(interval=None) / 100.0
        yield Observation(
            cpu_norm_percent,
            self._system_cpu_total_norm_pct_labels,
        )

    def _get_system_memory_actual_free(
        self,
        options: CallbackOptions,
    ) -> _Generator[Observation, None, None]:
        memory = _psutil.virtual_memory()
        yield Observation(
            memory.available,
            self._system_memory_actual_free_labels,
        )

    def _get_system_memory_total(
        self,
        options: CallbackOptions,
    ) -> _Generator[Observation, None, None]:
        memory = _psutil.virtual_memory()
        yield Observation(
            memory.total,
            self._system_memory_total_labels,
        )

    def _get_system_process_cpu_total_norm_pct(
        self,
        options: CallbackOptions,
    ) -> _Generator[Observation, None, None]:
        cpu_percent, _ = self._get_process_infos(p=self._process)
        yield Observation(
            cpu_percent / 100.0 / _psutil.cpu_count(),
            self._system_process_cpu_total_norm_pct_labels,
        )

    def _get_system_process_memory_size(
        self,
        options: CallbackOptions,
    ) -> _Generator[Observation, None, None]:
        _, memory_info = self._get_process_infos(p=self._process)
        yield Observation(
            memory_info.vms,
            self._system_process_memory_size_labels,
        )

    def _get_system_process_memory_rss_byte(
        self, options: CallbackOptions
    ) -> _Generator[Observation, None, None]:
        _, memory_info = self._get_process_infos(p=self._process)
        yield Observation(
            memory_info.rss,
            self._system_process_memory_rss_byte_labels,
        )


def _convert_os_headers(
    env_variable_name: str,
    default_headers: _Optional[_Dict[str, str]] = None,
) -> _Optional[_Dict[str, str]]:
    env_headers = _os.getenv(env_variable_name)
    if env_headers is None:
        return default_headers

    key_value_pairs = env_headers.split(",")
    result_dict: _Dict[str, str] = {}

    for pair in key_value_pairs:
        key, value = pair.split("=")
        result_dict[key] = value

    return result_dict


def _setup_traces(
    default_endpoint: str,
    resource: Resource,
    default_headers: _Optional[_Dict[str, str]] = None,
    certificate_file: _Optional[str] = None,
) -> None:
    """
    Set up traces for telemetry.

    Args:
        default_endpoint (str): The default endpoint for exporting traces.
        resource (Resource): The resource for exporting traces.
        default_headers (Dict[str, str], optional): The default headers for exporting traces.
        certificate_file (str, optional): The certificate file for exporting traces. Defaults to None.
    """

    endpoint = _os.environ.get(
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
        f"{default_endpoint}/v1/traces",
    )

    headers = _convert_os_headers(
        env_variable_name="OTEL_EXPORTER_OTLP_TRACES_HEADERS",
        default_headers=default_headers,
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
    resource: Resource,
    export_interval_millis: _Optional[float] = None,
    default_headers: _Optional[_Dict[str, str]] = None,
    certificate_file: _Optional[str] = None,
    configuration: _Optional[_Dict[str, _Optional[_List[str]]]] = None,
) -> None:
    """
    Set up metrics configuration for telemetry.

    Args:
        default_endpoint (str): The default endpoint for exporting metrics.
        resource (Resource): The resource for exporting traces.
        export_interval_millis (float, optional): The interval for exporting metrics. Defaults to None.
        default_headers (Dict[str, str], optional): The default headers for exporting traces.
        certificate_file (str, optional): The path to the certificate file. Defaults to None.
        configuration (Dict[str, List[str]], optional): The configuration for the metrics. Defaults to None.
    """

    endpoint = _os.environ.get(
        "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
        f"{default_endpoint}/v1/metrics",
    )

    headers = _convert_os_headers(
        env_variable_name="OTEL_EXPORTER_OTLP_METRICS_HEADERS",
        default_headers=default_headers,
    )

    exporter = OTLPMetricExporter(
        endpoint=endpoint,
        certificate_file=certificate_file,
        headers=headers,
    )
    reader = PeriodicExportingMetricReader(
        exporter=exporter,
        export_interval_millis=export_interval_millis,
    )
    provider = MeterProvider(
        resource=resource,
        metric_readers=[reader],
    )
    metrics.set_meter_provider(provider)

    SystemMetricsInstrumentor(config=configuration).instrument()


def _setup_logs(
    default_endpoint: str,
    resource: Resource,
    default_headers: _Optional[_Dict[str, str]] = None,
    certificate_file: _Optional[str] = None,
) -> LoggingHandler:
    """
    Set up logs for telemetry.

    Args:
        default_endpoint (str): The default endpoint for exporting logs.
        resource (Resource): The resource associated with the logs.
        default_headers (str, optional): The default headers for exporting logs. Defaults to None.
        certificate_file (str, optional): The path to the certificate file. Defaults to None.

    Returns:
        LoggingHandler: The logging handler for the telemetry logs.
    """

    endpoint = _os.environ.get(
        "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT",
        f"{default_endpoint}/v1/logs",
    )

    headers = _convert_os_headers(
        env_variable_name="OTEL_EXPORTER_OTLP_LOGS_HEADERS",
        default_headers=default_headers,
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


def setup_telemetry(config: _AlphaConfigSchema, app: _FastAPI) -> None:
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

    otel_exporter_otlp_headers = _convert_os_headers(
        env_variable_name="OTEL_EXPORTER_OTLP_HEADERS"
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

    resourceAttributes: Attributes = {
        SERVICE_NAME: otel_service_name,
        SERVICE_INSTANCE_ID: _platform.node(),
        SERVICE_VERSION: result_dict["service.version"],
        DEPLOYMENT_ENVIRONMENT: result_dict["deployment.environment"],
    }

    resource = Resource.create(resourceAttributes)

    _setup_traces(
        default_endpoint=otel_exporter_otlp_endpoint,
        certificate_file=otel_exporter_otl_certificate,
        default_headers=otel_exporter_otlp_headers,
        resource=resource,
    )

    _setup_metrics(
        export_interval_millis=config.api_config.apm.metrics_export_interval_millis,
        default_endpoint=otel_exporter_otlp_endpoint,
        certificate_file=otel_exporter_otl_certificate,
        default_headers=otel_exporter_otlp_headers,
        resource=resource,
        configuration=config.api_config.apm.configuration,
    )

    telemetry_handler = _setup_logs(
        default_endpoint=otel_exporter_otlp_endpoint,
        certificate_file=otel_exporter_otl_certificate,
        default_headers=otel_exporter_otlp_headers,
        resource=resource,
    )

    app.extra["telemetry_handler"] = telemetry_handler

    FastAPIInstrumentor().instrument_app(app)
