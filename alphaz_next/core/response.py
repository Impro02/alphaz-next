# MODULES
import json
from typing import Any, Dict, List, Optional, TypedDict, Union

# FASTAPI
from fastapi.responses import JSONResponse

# STARLETTE
from starlette.background import BackgroundTask

try:
    import ujson
except ImportError:  # pragma: nocover
    ujson = None  # type: ignore

try:
    import orjson
except ImportError:  # pragma: nocover
    orjson = None  # type: ignore


class ExtHeaders(TypedDict):
    pagination: Optional[str]
    status_description: Optional[Union[str, List[str]]]
    warning: Optional[bool]


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
        self._ext_headers = {}
        self._access_control_expose_headers = []

        if (pagination := ext_headers.get("pagination")) is not None:
            self._add_ext_header("x-pagination", pagination)
        if (status_description := ext_headers.get("status_description")) is not None:
            self._add_ext_header("x-status-description", json.dumps(status_description))
        if (warning := ext_headers.get("warning")) is not None:
            self._add_ext_header("x-warning", "1" if warning else "0")

        if self._ext_headers is not None:
            headers = headers or {}

            headers["access-control-expose-headers"] = ", ".join(
                [
                    *headers.get("access-control-expose-headers", "").split(", "),
                    *self._access_control_expose_headers,
                ]
            )

            headers.update(self._ext_headers)

        super().__init__(content, status_code, headers, media_type, background)

    def _add_ext_header(self, name: str, value: str) -> None:
        self._ext_headers[name] = value
        self._access_control_expose_headers.append(name)


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
