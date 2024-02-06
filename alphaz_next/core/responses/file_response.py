# MODULES
from os import PathLike as _PathLike, stat_result as _stat_result
from typing import Mapping as _Mapping

# FASTAPI
from fastapi.responses import FileResponse as _FileResponse

# STARLETTE
from starlette.background import BackgroundTask as _BackgroundTask

# CORE
from alphaz_next.core._base import (
    extend_headers as _extend_headers,
    ExtHeaders as _ExtHeaders,
)


class FileResponse(_FileResponse):
    """
    Represents a file response that can be returned by an HTTP endpoint.
    """

    def __init__(
        self,
        path: str | _PathLike[str],
        status_code: int = 200,
        headers: _Mapping[str, str] | None = None,
        ext_headers: _ExtHeaders | None = None,
        media_type: str | None = None,
        background: _BackgroundTask | None = None,
        filename: str | None = None,
        stat_result: _stat_result | None = None,
        method: str | None = None,
        content_disposition_type: str = "attachment",
    ) -> None:
        """
        Initializes a new instance of the FileResponse class.

        Args:
            path (str | PathLike[str]): The path to the file.
            status_code (int, optional): The HTTP status code. Defaults to 200.
            headers (Mapping[str, str] | None, optional): The HTTP headers. Defaults to None.
            ext_headers (ExtHeaders | None, optional): The extended HTTP headers. Defaults to None.
            media_type (str | None, optional): The media type of the file. Defaults to None.
            background (BackgroundTask | None, optional): The background task to run. Defaults to None.
            filename (str | None, optional): The filename of the file. Defaults to None.
            stat_result (stat_result | None, optional): The stat result of the file. Defaults to None.
            method (str | None, optional): The HTTP method. Defaults to None.
            content_disposition_type (str, optional): The content disposition type. Defaults to "attachment".
        """
        headers = _extend_headers(
            headers=headers,
            ext_headers=ext_headers,
        )

        super().__init__(
            path,
            status_code,
            headers,
            media_type,
            background,
            filename,
            stat_result,
            method,
            content_disposition_type,
        )
