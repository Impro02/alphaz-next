# MODULES
from typing import Mapping as _Mapping

# FASTAPI
from fastapi.responses import RedirectResponse as _RedirectResponse

# STARLETTE
from starlette.background import BackgroundTask as _BackgroundTask
from starlette.datastructures import URL as _URL

# CORE
from alphaz_next.core._base import (
    extend_headers as _extend_headers,
    ExtHeaders as _ExtHeaders,
)


class RedirectResponse(_RedirectResponse):
    """
    Represents a Redirect response that can be returned by an HTTP endpoint.
    """

    def __init__(
        self,
        url: str | _URL,
        status_code: int = 307,
        headers: _Mapping[str, str] | None = None,
        ext_headers: _ExtHeaders | None = None,
        background: _BackgroundTask | None = None,
    ) -> None:
        """
        Initializes a new instance of the RedirectResponse class.

        Args:
            url (str | URL): The URL to redirect to.
            status_code (int, optional): The HTTP status code for the redirect. Defaults to 307.
            headers (Mapping[str, str] | None, optional): Additional headers to include in the response. Defaults to None.
            ext_headers (ExtHeaders | None, optional): Extended headers to include in the response. Defaults to None.
            background (BackgroundTask | None, optional): Background task to run after the response is sent. Defaults to None.
        """
        headers = _extend_headers(
            headers=headers,
            ext_headers=ext_headers,
        )

        super().__init__(url, status_code, headers, background)
