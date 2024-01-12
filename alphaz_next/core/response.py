# MODULES
from typing import Any, Dict

# FASTAPI
from fastapi.responses import JSONResponse

# STARLETTE
from starlette.background import BackgroundTask

# CORE
from alphaz_next.core._base import extend_headers, ExtHeaders

try:
    import ujson
except ImportError:  # pragma: nocover
    ujson = None  # type: ignore

try:
    import orjson
except ImportError:  # pragma: nocover
    orjson = None  # type: ignore


class AlphaJSONResponse(JSONResponse):
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


class AlphaUJSONResponse(AlphaJSONResponse):
    def render(self, content: Any) -> bytes:
        assert ujson is not None, "ujson must be installed to use UJSONResponse"
        return ujson.dumps(content, ensure_ascii=False).encode("utf-8")


class AlphaORJSONResponse(AlphaJSONResponse):
    def render(self, content: Any) -> bytes:
        assert orjson is not None, "orjson must be installed to use ORJSONResponse"
        return orjson.dumps(
            content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY
        )
