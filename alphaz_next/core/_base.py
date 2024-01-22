# MODULES
import json
from typing import Dict, List, Optional, TypedDict, Union

from alphaz_next.core.constants import HeaderEnum


class ExtHeaders(TypedDict):
    pagination: Optional[str]
    status_description: Optional[Union[str, List[str]]]
    warning: Optional[bool]


def extend_headers(
    headers: Dict[str, str] | None = None,
    ext_headers: ExtHeaders | None = None,
) -> Optional[Dict[str, str]]:
    if ext_headers is None:
        return headers

    tmp_headers = {}

    access_control_expose_headers = []

    def add_ext_header(name: str, value: str) -> None:
        tmp_headers[name] = value
        access_control_expose_headers.append(name)

    if (pagination := ext_headers.get("pagination")) is not None:
        add_ext_header(HeaderEnum.PAGINATION.value, pagination)
    if (status_description := ext_headers.get("status_description")) is not None:
        add_ext_header(
            HeaderEnum.STATUS_DESCRIPTION.value, json.dumps(status_description)
        )
    if (warning := ext_headers.get("warning")) is not None:
        add_ext_header(HeaderEnum.WARNING.value, "1" if warning else "0")

    if tmp_headers is not None:
        headers = headers or {}

        headers["access-control-expose-headers"] = ", ".join(
            [
                *headers.get("access-control-expose-headers", "").split(", "),
                *access_control_expose_headers,
            ]
        )

        headers.update(tmp_headers)

    return headers
