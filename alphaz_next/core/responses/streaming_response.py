# MODULES
from typing import Mapping as _Mapping

# FASTAPI
from fastapi.responses import StreamingResponse as _StreamingResponse

# STARLETTE
from starlette.background import BackgroundTask as _BackgroundTask
from starlette.responses import ContentStream as _ContentStream

# CORE
from alphaz_next.core._base import (
    extend_headers as _extend_headers,
    ExtHeaders as _ExtHeaders,
)


class StreamingResponse(_StreamingResponse):
    """
    Represents a StreamingResponse that can be returned by an HTTP endpoint.
    """

    def __init__(
        self,
        content: _ContentStream,
        status_code: int = 200,
        headers: _Mapping[str, str] | None = None,
        ext_headers: _ExtHeaders | None = None,
        media_type: str | None = None,
        background: _BackgroundTask | None = None,
    ) -> None:
        """
        Initializes a new instance of the StreamingResponse class.

        Args:
            content (ContentStream): The content stream to be streamed.
            status_code (int, optional): The HTTP status code. Defaults to 200.
            headers (Mapping[str, str] | None, optional): The HTTP headers. Defaults to None.
            ext_headers (ExtHeaders | None, optional): The extended headers. Defaults to None.
            media_type (str | None, optional): The media type of the content. Defaults to None.
            background (BackgroundTask | None, optional): The background task to run. Defaults to None.
        """
        headers = _extend_headers(
            headers=headers,
            ext_headers=ext_headers,
        )

        super().__init__(content, status_code, headers, media_type, background)
