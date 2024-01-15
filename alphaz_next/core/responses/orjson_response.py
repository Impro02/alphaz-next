# MODULES
from typing import Any, Dict

# FASTAPI
from fastapi.responses import ORJSONResponse as _ORJSONResponse

# STARLETTE
from starlette.background import BackgroundTask

# CORE
from alphaz_next.core._base import extend_headers, ExtHeaders


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
