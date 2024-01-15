# MODULES
from typing import Any, Dict, Mapping

# FASTAPI
from fastapi.responses import (
    JSONResponse as _JSONResponse,
    UJSONResponse as _UJSONResponse,
    ORJSONResponse as _ORJSONResponse,
    Response as _Response,
)

# STARLETTE
from starlette.background import BackgroundTask

# CORE
from alphaz_next.core._base import extend_headers, ExtHeaders


class Response(_Response):
    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        ext_headers: ExtHeaders | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        headers = extend_headers(
            headers=headers,
            ext_headers=ext_headers,
        )

        super().__init__(content, status_code, headers, media_type, background)


class JSONResponse(_JSONResponse):
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Dict[str, str] | None = None,
        ext_headers: ExtHeaders | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        headers = extend_headers(
            headers=headers,
            ext_headers=ext_headers,
        )

        super().__init__(content, status_code, headers, media_type, background)


class UJSONResponse(_UJSONResponse):
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Dict[str, str] | None = None,
        ext_headers: ExtHeaders | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        headers = extend_headers(
            headers=headers,
            ext_headers=ext_headers,
        )

        super().__init__(content, status_code, headers, media_type, background)


class ORJSONResponse(_ORJSONResponse):
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Dict[str, str] | None = None,
        ext_headers: ExtHeaders | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        headers = extend_headers(
            headers=headers,
            ext_headers=ext_headers,
        )

        super().__init__(content, status_code, headers, media_type, background)
