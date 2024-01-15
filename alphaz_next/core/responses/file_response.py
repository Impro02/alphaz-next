# MODULES
from os import PathLike, stat_result
from typing import Mapping

# FASTAPI
from fastapi.responses import FileResponse as _FileResponse

# STARLETTE
from starlette.background import BackgroundTask

# CORE
from alphaz_next.core._base import extend_headers, ExtHeaders


class FileResponse(_FileResponse):
    def __init__(
        self,
        path: str | PathLike[str],
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        ext_headers: ExtHeaders | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        filename: str | None = None,
        stat_result: stat_result | None = None,
        method: str | None = None,
        content_disposition_type: str = "attachment",
    ) -> None:
        headers = extend_headers(
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
