# MODULES
from typing import (
    Annotated as _Annotated,
    Any as _Any,
    Dict as _Dict,
    List as _List,
    Type,
    TypeVar,
)

# FASTAPI
from fastapi import Depends as _Depends, status as _status
from fastapi.security import (
    APIKeyHeader as _APIKeyHeader,
    OAuth2PasswordBearer as _OAuth2PasswordBearer,
    SecurityScopes as _SecurityScopes,
)

# JOSE
from jose import JWTError as _JWTError, jwt as _jwt

# LIBS
from alphaz_next.libs.httpx import (
    make_async_request_with_retry as _make_async_request_with_retry,
    post_process_http_response as _post_process_http_response,
)

# MODELS
from alphaz_next.models.auth.user import UserBaseSchema as _UserBaseSchema
from alphaz_next.models.config._base.internal_config_settings import (
    create_internal_config as _create_internal_config,
)

# EXCEPTIONS
from alphaz_next.core.exceptions import (
    InvalidCredentialsError as _InvalidCredentialsError,
    NotEnoughPermissionsError as _NotEnoughPermissionsError,
    HTTPException as _HTTPException,
)

INTERNAL_CONFIG = _create_internal_config()

API_KEY_HEADER = _APIKeyHeader(name="api_key", auto_error=False)
OAUTH2_SCHEME = _OAuth2PasswordBearer(tokenUrl=INTERNAL_CONFIG.token_url)

_T = TypeVar("_T", bound=_UserBaseSchema)


def decode_token(token: str) -> _Dict[str, _Any]:
    """
    Decode a JWT token and return the payload.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Dict[str, Any]: The decoded payload.

    Raises:
        InvalidCredentialsError: If the token is invalid or does not contain a valid username.
    """
    try:
        payload = _jwt.decode(
            token,
            INTERNAL_CONFIG.secret_key,
            algorithms=[INTERNAL_CONFIG.algorithm],
        )
    except _JWTError:
        raise _InvalidCredentialsError()

    username: str = payload.get("sub")
    if username is None:
        raise _InvalidCredentialsError()

    return payload


async def get_user(token: str, schema: Type[_T]) -> _T:
    """
    Retrieves user information using the provided token.

    Args:
        token (str): The authentication token.
        schema (Type[_T]): The schema type to validate the response against.

    Returns:
        _T: The user information.

    Raises:
        Any: Any exception raised during the request or response processing.
    """
    decode_token(token=token)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = await _make_async_request_with_retry(
        method="POST",
        url=INTERNAL_CONFIG.user_me_url,
        **{
            "headers": headers,
        },
    )

    return _post_process_http_response(
        response,
        schema=schema,
    )


async def get_api_key(api_key: str, schema: Type[_T]) -> _T:
    """
    Retrieves the API key using the provided `api_key` and returns the processed response.

    Args:
        api_key (str): The API key to be used for authentication.
        schema (Type[_T]): The type of the response schema.

    Returns:
        _T: The processed response based on the provided schema.
    """
    headers = {
        "api_key": api_key,
    }

    response = await _make_async_request_with_retry(
        method="POST",
        url=INTERNAL_CONFIG.api_key_me_url,
        **{
            "headers": headers,
        },
    )

    return _post_process_http_response(
        response,
        schema=schema,
    )


def check_user_permissions(
    permissions: _List[str],
    user_permissions: _List[str],
) -> None:
    """
    Check if the user has the required permissions.

    Args:
        permissions (List[str]): The list of required permissions.
        user_permissions (List[str]): The list of permissions the user has.

    Raises:
        NotEnoughPermissionsError: If the user does not have all the required permissions.
    """
    if len(permissions) > 0 and not any(
        [user_permission in permissions for user_permission in user_permissions]
    ):
        raise _NotEnoughPermissionsError()


async def get_user_from_jwt(
    schema: Type[_T],
    security_scopes: _SecurityScopes,
    token: _Annotated[str, _Depends(OAUTH2_SCHEME)],
) -> _T:
    """
    Retrieves a user from a JWT token and performs permission checks.

    Args:
        schema (Type[_T]): The schema type used to deserialize the user data.
        security_scopes (_SecurityScopes): The security scopes required for the user.
        token (_Annotated[str, _Depends(OAUTH2_SCHEME)]): The JWT token.

    Returns:
        _T: The deserialized user object.

    Raises:
        _HTTPException: If the credentials are invalid or the user does not have enough permissions.
    """

    try:
        user = await get_user(token=token, schema=schema)

        check_user_permissions(
            permissions=security_scopes.scopes,
            user_permissions=user.permissions,
        )

        return user

    except _InvalidCredentialsError as ex:
        raise _HTTPException(
            status_code=_status.HTTP_401_UNAUTHORIZED,
            headers={
                "WWW-Authenticate": "Bearer",
            },
            ext_headers={
                "status_description": ex.args,
            },
        )
    except _NotEnoughPermissionsError as ex:
        raise _HTTPException(
            status_code=_status.HTTP_403_FORBIDDEN,
            headers={
                "WWW-Authenticate": "Bearer",
            },
            ext_headers={
                "status_description": ex.args,
            },
        )


async def get_user_from_api_key(
    schema: Type[_T],
    security_scopes: _SecurityScopes,
    api_key: _Annotated[
        str,
        _Depends(API_KEY_HEADER),
    ],
) -> _T:
    """
    Retrieves a user from the API key.

    Args:
        schema (Type[_T]): The schema type.
        security_scopes (_SecurityScopes): The security scopes.
        api_key (_Annotated[str, _Depends(API_KEY_HEADER)]): The API key.

    Returns:
        _T: The user retrieved from the API key.

    Raises:
        _HTTPException: If the credentials are invalid or the user doesn't have enough permissions.
    """

    try:
        if api_key is None:
            raise _InvalidCredentialsError()

        user = await get_api_key(api_key=api_key, schema=schema)

        check_user_permissions(
            permissions=security_scopes.scopes,
            user_permissions=user.permissions,
        )

        return user

    except _InvalidCredentialsError as ex:
        raise _HTTPException(
            status_code=_status.HTTP_401_UNAUTHORIZED,
            headers={
                "WWW-Authenticate": "Bearer",
            },
            ext_headers={
                "status_description": ex.args,
            },
        )
    except _NotEnoughPermissionsError as ex:
        raise _HTTPException(
            status_code=_status.HTTP_403_FORBIDDEN,
            headers={
                "WWW-Authenticate": "Bearer",
            },
            ext_headers={
                "status_description": ex.args,
            },
        )
