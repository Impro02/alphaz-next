# MODULES
from typing import Any, Dict

# FASTAPI
from fastapi.exceptions import HTTPException as _HTTPException

# CORE
from alphaz_next.core._base import extend_headers, ExtHeaders


class InvalidCredentialsError(Exception):
    """Exception raised for invalid credentials.

    Attributes:
        None
    """

    def __init__(self):
        super().__init__("Could not validate credentials")


class NotEnoughPermissionsError(Exception):
    """Exception raised when there are not enough permissions."""

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
        """
        Initialize a new HTTPException.

        Args:
            status_code (int): The HTTP status code.
            detail (Any, optional): Additional detail about the exception. Defaults to None.
            headers (Dict[str, str] | None, optional): Additional headers to include in the response. Defaults to None.
            ext_headers (ExtHeaders | None, optional): Extended headers to include in the response. Defaults to None.
        """
        headers = extend_headers(
            headers=headers,
            ext_headers=ext_headers,
        )

        super().__init__(status_code, detail, headers)
