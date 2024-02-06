from fastapi.encoders import jsonable_encoder as _jsonable_encoder
from fastapi.exceptions import (
    RequestValidationError as _RequestValidationError,
    WebSocketRequestValidationError as _WebSocketRequestValidationError,
)
from fastapi.utils import (
    is_body_allowed_for_status_code as _is_body_allowed_for_status_code,
)
from fastapi.websockets import WebSocket as _WebSocket
from starlette.exceptions import HTTPException as _HTTPException
from starlette.requests import Request as _Request
from starlette.responses import JSONResponse as _JSONResponse, Response as _Response
from starlette.status import (
    HTTP_422_UNPROCESSABLE_ENTITY as _HTTP_422_UNPROCESSABLE_ENTITY,
    WS_1008_POLICY_VIOLATION as _WS_1008_POLICY_VIOLATION,
)


async def http_exception_handler(request: _Request, exc: _HTTPException) -> _Response:
    """
    Handle HTTP exceptions and return a response.

    Args:
        request (Request): The incoming request.
        exc (HTTPException): The raised HTTP exception.

    Returns:
        Response: The response to be sent back to the client.
    """
    headers = getattr(exc, "headers", None)
    if not _is_body_allowed_for_status_code(exc.status_code):
        return _Response(status_code=exc.status_code, headers=headers)
    return _JSONResponse(
        {"detail": exc.detail}, status_code=exc.status_code, headers=headers
    )


async def request_validation_exception_handler(
    request: _Request, exc: _RequestValidationError
) -> _JSONResponse:
    """
    Exception handler for request validation errors.

    Args:
        request (Request): The incoming request.
        exc (RequestValidationError): The validation error.

    Returns:
        JSONResponse: The JSON response with the validation error details.
    """
    return _JSONResponse(
        status_code=_HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": _jsonable_encoder(exc.errors())},
    )


async def websocket_request_validation_exception_handler(
    websocket: _WebSocket, exc: _WebSocketRequestValidationError
) -> None:
    """
    Handles the exception raised when there is a validation error in a WebSocket request.

    Args:
        websocket (WebSocket): The WebSocket connection.
        exc (WebSocketRequestValidationError): The exception object containing the validation errors.

    Returns:
        None
    """
    await websocket.close(
        code=_WS_1008_POLICY_VIOLATION, reason=_jsonable_encoder(exc.errors())
    )
