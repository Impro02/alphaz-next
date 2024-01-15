# MODULES
from typing import Mapping

# FASTAPI
from fastapi.responses import RedirectResponse as _RedirectResponse

# STARLETTE
from starlette.background import BackgroundTask
from starlette.datastructures import URL

# CORE
from alphaz_next.core._base import extend_headers, ExtHeaders


class RedirectResponse(_RedirectResponse):
    def __init__(
        self,
        url: str | URL,
        status_code: int = 307,
        headers: Mapping[str, str] | None = None,
        ext_headers: ExtHeaders | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        headers = extend_headers(
            headers=headers,
            ext_headers=ext_headers,
        )

        super().__init__(url, status_code, headers, background)
