# MODULES
from typing import Dict, List, Optional, Sequence

# FASTAPI
from fastapi import APIRouter, FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi, BaseRoute
from fastapi.middleware.cors import CORSMiddleware

# DEPENDENCY_INJECTOR
from dependency_injector import containers
from fastapi.responses import HTMLResponse, RedirectResponse


# MODELS
from alphaz_next.models.config.alpha_config import AlphaConfigSchema

# ELASTICAPM
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

_DEFAULT_FAVICON_URL = "https://fastapi.tiangolo.com/img/favicon.png"


def _custom_openapi(config: AlphaConfigSchema, routes: List[BaseRoute]):
    title = config.project_name.upper()
    if config.environment.lower() != "prod":
        title = f"{title} [{config.environment.upper()}]"

    openapi_dict = {}
    if (openapi_config := config.api_config.openapi) is not None:
        openapi_dict["description"] = openapi_config.description

        if openapi_config.contact is not None:
            openapi_dict["contact"] = {
                "name": config.api_config.openapi.contact.name,
                "email": config.api_config.openapi.contact.email,
            }

    openapi_schema = get_openapi(
        title=title,
        version=config.version,
        routes=routes,
        **openapi_dict,
    )

    return openapi_schema


def create_app(
    config: AlphaConfigSchema,
    routers: List[APIRouter],
    container: Optional[containers.DeclarativeContainer] = None,
    allow_origins: Sequence[str] = (),
    allow_methods: Sequence[str] = ("GET",),
    allow_headers: Sequence[str] = (),
    allow_credentials: bool = False,
    status_response: Dict = {"status": "OK"},
) -> FastAPI:
    # APP
    app = FastAPI(
        title=config.project_name.upper(),
        version=config.version,
        docs_url=None,
        redoc_url=None,
    )
    app.container = container

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
    )

    if config.api_config.apm is not None and config.api_config.apm.active:
        apm = make_apm_client(
            {
                "SERVICE_NAME": config.project_name,
                "ENVIRONMENT": config.api_config.apm.environment,
                "SERVER_URL": config.api_config.apm.server_url,
                "SERVER_CERT": config.api_config.apm.ssl_ca_cert,
                "VERIFY_SERVER_CERT": config.api_config.apm.ssl_verify,
            }
        )

        app.add_middleware(ElasticAPM, client=apm)

    for router in routers:
        app.include_router(router)

    app.openapi_schema = _custom_openapi(config=config, routes=app.routes)

    swagger_favicon_url = _DEFAULT_FAVICON_URL
    redoc_favicon_url = _DEFAULT_FAVICON_URL
    if (openapi_config := config.api_config.openapi) is not None:
        if openapi_config.swagger_favicon_url:
            swagger_favicon_url = openapi_config.swagger_favicon_url

        if openapi_config.redoc_favicon_url:
            redoc_favicon_url = openapi_config.redoc_favicon_url

    @app.get("/status", include_in_schema=False)
    async def get_api_status():
        return status_response

    @app.get("/docs", include_in_schema=False)
    def swagger_ui_html(req: Request) -> HTMLResponse:
        root_path = req.scope.get("root_path", "").rstrip("/")
        openapi_url = root_path + app.openapi_url
        oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url
        if oauth2_redirect_url:
            oauth2_redirect_url = root_path + oauth2_redirect_url

        return get_swagger_ui_html(
            openapi_url=openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=oauth2_redirect_url,
            init_oauth=app.swagger_ui_init_oauth,
            swagger_favicon_url=swagger_favicon_url,
            swagger_ui_parameters=app.swagger_ui_parameters,
        )

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_favicon_url=redoc_favicon_url,
        )

    @app.get("/")
    async def home():
        return RedirectResponse("/docs")

    return app
