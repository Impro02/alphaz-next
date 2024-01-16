# MODULES
from typing import List, Optional, Sequence

# FASTAPI
from fastapi import APIRouter, FastAPI
from fastapi.openapi.utils import get_openapi, BaseRoute
from fastapi.middleware.cors import CORSMiddleware

# DEPENDENCY_INJECTOR
from dependency_injector import containers


# MODELS
from alphaz_next.models.config.alpha_config import AlphaConfigSchema

# ELASTICAPM
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM


def _custom_openapi(config: AlphaConfigSchema, routes: List[BaseRoute]):
    title = config.project_name.upper()
    if config.environment.lower() != "prod":
        title = f"{title} [{config.environment.upper()}]"

    openapi_schema = get_openapi(
        title=title,
        version=config.version,
        description=config.api_config.openapi.description,
        contact={
            "name": config.api_config.openapi.contact.name,
            "email": config.api_config.openapi.contact.email,
        },
        routes=routes,
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

    return app
