# MODULES
import os
import sys as _sys
from typing import (
    Any as _Any,
    AsyncContextManager as _AsyncContextManager,
    Dict as _Dict,
    List as _List,
    Optional as _Optional,
    Sequence as _Sequence,
    Union as _Union,
)
import logging
from loguru import logger

# FASTAPI
from fastapi import (
    APIRouter as _APIRouter,
    FastAPI as _FastAPI,
    HTTPException as _HTTPException,
    Request as _Request,
    Response as _Response,
)
from fastapi.exceptions import RequestValidationError as _RequestValidationError
from fastapi.exception_handlers import http_exception_handler as _http_exception_handler
from fastapi.exception_handlers import (
    request_validation_exception_handler as _request_validation_exception_handler,
)
from fastapi.openapi.docs import (
    get_swagger_ui_html as _get_swagger_ui_html,
    get_redoc_html as _get_redoc_html,
)
from fastapi.openapi.utils import get_openapi as _get_openapi, BaseRoute as _BaseRoute
from fastapi.responses import (
    HTMLResponse as _HTMLResponse,
    JSONResponse as _JSONResponse,
    PlainTextResponse as _PlainTextResponse,
    RedirectResponse as _RedirectResponse,
)

# OPENTELEMETRY
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# MODELS
from alphaz_next.models.config.alpha_config import (
    AlphaConfigSchema as _AlphaConfigSchema,
)

# CORE
from alphaz_next.core._middleware import (
    log_request_middleware as _log_request_middleware,
    CORSMiddleware as _CORSMiddleware,
)


# ELASTICAPM

_DEFAULT_FAVICON_URL = "https://fastapi.tiangolo.com/img/favicon.png"

_uvicorn_access = logging.getLogger("uvicorn.access")
_uvicorn_access.disabled = True

uvicorn_logger = logger.bind(service="uvicorn")


def _custom_openapi(
    config: _AlphaConfigSchema, routes: _List[_BaseRoute]
) -> _Dict[str, _Any]:
    """
    Generate a custom OpenAPI schema based on the provided configuration and routes.

    Args:
        config (AlphaConfigSchema): The configuration object containing project settings.
        routes (List[BaseRoute]): The list of routes to include in the OpenAPI schema.

    Returns:
        Dict[str, Any]: The generated OpenAPI schema.
    """
    title = config.project_name.upper()
    if config.environment.lower() != "prod":
        title = f"{title} [{config.environment.upper()}]"

    openapi_dict = {}
    if (openapi_config := config.api_config.openapi) is not None:
        openapi_dict["description"] = openapi_config.description
        openapi_dict["tags"] = openapi_config.tags

        if openapi_config.contact is not None:
            openapi_dict["contact"] = {
                "name": config.api_config.openapi.contact.name,
                "email": config.api_config.openapi.contact.email,
            }

    openapi_schema = _get_openapi(
        title=title,
        version=config.version,
        routes=routes,
        **openapi_dict,
    )

    return openapi_schema


def _setup_opentelemetry(config: _AlphaConfigSchema, app: _FastAPI) -> None:
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

    otel_exporter_otlp_headers = os.environ.get(
        "OTEL_EXPORTER_OTLP_HEADERS",
        None,
    )

    otel_exporter_otlp_endpoint = os.environ.get(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        apm_server_url,
    )

    otel_exporter_otl_certificate = os.environ.get(
        "OTEL_EXPORTER_OTLP_CERTIFICATE",
        certificate_path,
    )

    # Ressource
    resource_attributes = (
        os.environ.get("OTEL_RESOURCE_ATTRIBUTES")
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

    # Traces
    otel_exported_otlp_traces_endpoint = os.environ.get(
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
        f"{otel_exporter_otlp_endpoint}/v1/traces",
    )

    exporter = OTLPSpanExporter(
        endpoint=otel_exported_otlp_traces_endpoint,
        certificate_file=otel_exporter_otl_certificate,
        headers=otel_exporter_otlp_headers,
    )

    processor = BatchSpanProcessor(exporter)
    traceProvider = TracerProvider(resource=resource)
    traceProvider.add_span_processor(processor)
    trace.set_tracer_provider(traceProvider)

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(processor)

    # Metrics
    otel_exported_otlp_metrics_endpoint = os.environ.get(
        "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
        f"{otel_exporter_otlp_endpoint}/v1/metrics",
    )
    exporter = OTLPMetricExporter(
        endpoint=otel_exported_otlp_metrics_endpoint,
        certificate_file=otel_exporter_otl_certificate,
        headers=otel_exporter_otlp_headers,
    )
    reader = PeriodicExportingMetricReader(exporter=exporter)
    meterProvider = MeterProvider(
        resource=resource,
        metric_readers=[reader],
    )
    metrics.set_meter_provider(meterProvider)

    FastAPIInstrumentor().instrument_app(app)


def create_app(
    config: _AlphaConfigSchema,
    routes: _Optional[_BaseRoute] = None,
    routers: _Optional[_List[_APIRouter]] = None,
    lifespan: _Optional[_AsyncContextManager] = None,
    allow_origins: _Sequence[str] = (),
    allow_methods: _Sequence[str] = ("GET",),
    allow_headers: _Sequence[str] = (),
    allow_credentials: bool = False,
    allow_private_network: bool = False,
    status_response: _Dict = {"status": "OK"},
) -> _FastAPI:
    """
    Create a FastAPI application with the specified configuration.

    Args:
        config (AlphaConfigSchema): The configuration for the application.
        routes (Optional[BaseRoute]): The list of routes to include in the application. Defaults to None.
        routers (List[APIRouter]): The list of API routers to include in the application.
        container (Optional[containers.DeclarativeContainer]): The dependency injection container. Defaults to None.
        allow_origins (Sequence[str]): The list of allowed origins for CORS. Defaults to ().
        allow_methods (Sequence[str]): The list of allowed HTTP methods for CORS. Defaults to ("GET",).
        allow_headers (Sequence[str]): The list of allowed headers for CORS. Defaults to ().
        allow_credentials (bool): Whether to allow credentials for CORS. Defaults to False.
        allow_private_network (bool): Whether to allow private network for CORS. Defaults to False.
        status_response (Dict): The response to return for the "/status" endpoint. Defaults to {"status": "OK"}.

    Returns:
        FastAPI: The created FastAPI application.
    """

    if config.api_config.logging is not None:
        uvicorn_logger.add(
            _sys.stderr,
            level=config.api_config.logging.level.upper(),
            filter=lambda record: all(
                [
                    record["extra"].get("service") == "uvicorn",
                    record["extra"].get("endpoint")
                    not in config.api_config.logging.excluded_routers,
                ]
            ),
            colorize=True,
        )

    # APP
    app = _FastAPI(
        routes=routes,
        title=config.project_name.upper(),
        version=config.version,
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(
        _CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        allow_private_network=allow_private_network,
    )

    app.middleware("http")(_log_request_middleware)

    _setup_opentelemetry(config=config, app=app)

    [app.include_router(router) for router in routers or []]

    app.openapi_schema = _custom_openapi(config=config, routes=app.routes)

    swagger_favicon_url = _DEFAULT_FAVICON_URL
    redoc_favicon_url = _DEFAULT_FAVICON_URL
    if (openapi_config := config.api_config.openapi) is not None:
        if openapi_config.swagger_favicon_url:
            swagger_favicon_url = openapi_config.swagger_favicon_url

        if openapi_config.redoc_favicon_url:
            redoc_favicon_url = openapi_config.redoc_favicon_url

    @app.exception_handler(_RequestValidationError)
    async def request_validation_exception_handler(
        request: _Request, exc: _RequestValidationError
    ) -> _JSONResponse:
        """
        This is a wrapper to the default RequestValidationException handler of FastAPI.
        This function will be called when client input is not valid.
        """
        body = await request.body()
        query_params = request.query_params._dict
        detail = {
            "errors": exc.errors(),
            "body": body.decode(),
            "query_params": query_params,
        }

        with uvicorn_logger.contextualize(endpoint=request.base_url):
            uvicorn_logger.info(detail)
        return await _request_validation_exception_handler(request, exc)

    @app.exception_handler(_HTTPException)
    async def http_exception_handler(
        request: _Request, exc: _HTTPException
    ) -> _Union[_JSONResponse, _Response]:
        """
        This is a wrapper to the default HTTPException handler of FastAPI.
        This function will be called when a HTTPException is explicitly raised.
        """
        return await _http_exception_handler(request, exc)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: _Request, exc: Exception
    ) -> _PlainTextResponse:
        """
        This middleware will log all unhandled exceptions.
        Unhandled exceptions are all exceptions that are not HTTPExceptions or RequestValidationErrors.
        """
        host = getattr(getattr(request, "client", None), "host", None)
        port = getattr(getattr(request, "client", None), "port", None)
        url = (
            f"{request.url.path}?{request.query_params}"
            if request.query_params
            else request.url.path
        )
        exception_type, exception_value, exception_traceback = _sys.exc_info()
        exception_name = getattr(exception_type, "__name__", None)

        with uvicorn_logger.contextualize(endpoint=request.base_url):
            uvicorn_logger.error(
                f'{host}:{port} - "{request.method} {url}" 500 Internal Server Error <{exception_name}: {exception_value}>'
            )
        return _PlainTextResponse(str(exc), status_code=500)

    @app.get("/status", include_in_schema=False)
    async def get_api_status():
        return status_response

    @app.get("/docs", include_in_schema=False)
    def swagger_ui_html(req: _Request) -> _HTMLResponse:
        root_path = req.scope.get("root_path", "").rstrip("/")
        openapi_url = root_path + app.openapi_url
        oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url
        if oauth2_redirect_url:
            oauth2_redirect_url = root_path + oauth2_redirect_url

        return _get_swagger_ui_html(
            openapi_url=openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=oauth2_redirect_url,
            init_oauth=app.swagger_ui_init_oauth,
            swagger_favicon_url=swagger_favicon_url,
            swagger_ui_parameters=app.swagger_ui_parameters,
        )

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return _get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_favicon_url=redoc_favicon_url,
        )

    @app.get("/")
    async def home():
        return _RedirectResponse("/docs")

    return app
