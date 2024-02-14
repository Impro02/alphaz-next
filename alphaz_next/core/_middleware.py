# MODULES
import http
import time
from typing import Any, Awaitable, Callable, MutableMapping, Sequence

# FASTAPI
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware as _CORSMiddleware

# CORE
from alphaz_next.core.constants import HeaderEnum
from alphaz_next.core.uvicorn_logger import UVICORN_LOGGER


class CORSMiddleware(_CORSMiddleware):
    def __init__(
        self,
        app: Callable[
            [
                MutableMapping[str, Any],
                Callable[[], Awaitable[MutableMapping[str, Any]]],
                Callable[[MutableMapping[str, Any]], Awaitable[None]],
            ],
            Awaitable[None],
        ],
        allow_origins: Sequence[str] = ...,
        allow_methods: Sequence[str] = ...,
        allow_headers: Sequence[str] = ...,
        allow_private_network: bool = False,
        allow_credentials: bool = False,
        allow_origin_regex: str | None = None,
        expose_headers: Sequence[str] = ...,
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
            ] = True


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

    UVICORN_LOGGER.info(
        f'{host}:{port} - "{request.method} {url}" {response.status_code} {status_phrase} {formatted_process_time}ms'
    )
    return response
