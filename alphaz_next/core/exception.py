# MODULES
from typing import Any, Dict

# FASTAPI
from fastapi.exceptions import HTTPException as _HTTPException

# CORE
from alphaz_next.core._base import extend_headers, ExtHeaders


class InvalidCredentialsError(Exception):
    def __init__(self):
        super().__init__("Could not validate credentials")


class NotEnoughPermissionsError(Exception):
    def __init__(self):
        super().__init__("Not enough permissions")


class HTTPException(_HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Dict[str, str] | None = None,
        ext_headers: ExtHeaders | None = None,
    ) -> None:
        headers = extend_headers(
            headers=headers,
            ext_headers=ext_headers,
        )

        super().__init__(status_code, detail, headers)
