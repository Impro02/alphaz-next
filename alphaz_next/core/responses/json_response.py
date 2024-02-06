# MODULES
from typing import Any as _Any, Dict as _Dict

# FASTAPI
from fastapi.responses import JSONResponse as _JSONResponse

# STARLETTE
from starlette.background import BackgroundTask as _BackgroundTask

# CORE
from alphaz_next.core._base import (
    extend_headers as _extend_headers,
    ExtHeaders as _ExtHeaders,
)


class JSONResponse(_JSONResponse):
    """
    Represents a JSON response that can be returned by an HTTP endpoint.
    """

    def __init__(
        self,
        content: _Any,
        status_code: int = 200,
        headers: _Dict[str, str] | None = None,
        ext_headers: _ExtHeaders | None = None,
        media_type: str | None = None,
        background: _BackgroundTask | None = None,
    ) -> None:
        """
        Initializes a new instance of the JSONResponse class.

        Args:
            content (Any): The content of the response.
            status_code (int, optional): The HTTP status code of the response. Defaults to 200.
            headers (Dict[str, str] | None, optional): The headers of the response. Defaults to None.
            ext_headers (ExtHeaders | None, optional): The extended headers of the response. Defaults to None.
            media_type (str | None, optional): The media type of the response. Defaults to None.
            background (BackgroundTask | None, optional): The background task associated with the response. Defaults to None.
        """
        headers = _extend_headers(
            headers=headers,
            ext_headers=ext_headers,
        )

        super().__init__(content, status_code, headers, media_type, background)
