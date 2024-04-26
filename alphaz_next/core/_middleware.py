# MODULES
import http
import logging as _logging
import time
from typing import Optional, Sequence

# FASTAPI
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware as _CORSMiddleware

# STARLETTE
from starlette.types import ASGIApp

# CORE
from alphaz_next.core.constants import HeaderEnum

uvicorn_logger = _logging.getLogger("uvicorn")


class CORSMiddleware(_CORSMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        allow_origins: Sequence[str] = (),
        allow_methods: Sequence[str] = ("GET",),
        allow_headers: Sequence[str] = (),
        allow_credentials: bool = False,
        allow_private_network: bool = False,
        allow_origin_regex: Optional[str] = None,
        expose_headers: Sequence[str] = (),
        max_age: int = 600,
    ) -> None:
        super().__init__(
            app,
            allow_origins,
            allow_methods,
            allow_headers,
            allow_credentials,
            allow_origin_regex,
            expose_headers,
            max_age,
        )

        if allow_private_network:
            self.simple_headers[
                HeaderEnum.ACCESS_CONTROL_ALLOW_PRIVATE_NETWORK.value
            ] = "true"
            self.preflight_headers[
                HeaderEnum.ACCESS_CONTROL_ALLOW_PRIVATE_NETWORK.value
            ] = "true"


async def log_request_middleware(request: Request, call_next):
    """
    This middleware will log all requests and their processing time.
    E.g. log:
    0.0.0.0:1234 - GET /ping 200 OK 1.00ms
    """
    url = (
        f"{request.url.path}?{request.query_params}"
        if request.query_params
        else request.url.path
    )
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    try:
        status_phrase = http.HTTPStatus(response.status_code).phrase
    except ValueError:
        status_phrase = ""

    response.headers[HeaderEnum.PROCESS_TIME.value] = str(process_time)

    uvicorn_logger.info(
        f'{host}:{port} - "{request.method} {url}" {response.status_code} {status_phrase} {formatted_process_time}ms'
    )
    return response
