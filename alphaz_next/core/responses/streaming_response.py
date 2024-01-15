# MODULES
from typing import Mapping

# FASTAPI
from fastapi.responses import StreamingResponse as _StreamingResponse

# STARLETTE
from starlette.background import BackgroundTask
from starlette.responses import ContentStream

# CORE
from alphaz_next.core._base import extend_headers, ExtHeaders


class StreamingResponse(_StreamingResponse):
    def __init__(
        self,
        content: ContentStream,
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
