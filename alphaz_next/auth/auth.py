# MODULES
from typing import Annotated as _Annotated, Any as _Any, Dict as _Dict, List as _List

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
from alphaz_next.models.auth.user import (
    UserSchema as _UserSchema,
    UserShortSchema as _UserShortSchema,
)
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


async def get_user(token: str) -> _UserSchema:
    """
    Retrieves user information using the provided token.

    Args:
        token (str): The authentication token.

    Returns:
        UserSchema: The user information.

    Raises:
        Exception: If there is an error retrieving the user information.
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
        schema=_UserSchema,
    )


async def get_api_key(api_key: str) -> _UserShortSchema:
    """
    Retrieves user information using the provided API key.

    Args:
        api_key (str): The API key for authentication.

    Returns:
        UserShortSchema: The user information.

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
        schema=_UserShortSchema,
    )


def check_user_permissions(
    permissions: _List[str], user_permissions: _List[str]
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
    security_scopes: _SecurityScopes,
    token: _Annotated[str, _Depends(OAUTH2_SCHEME)],
) -> _UserSchema:
    """
    Retrieves the user from the JWT token and performs permission checks.

    Args:
        security_scopes (SecurityScopes): The security scopes required for the endpoint.
        token (str): The JWT token.

    Returns:
        UserSchema: The user object.

    Raises:
        HTTPException: If the credentials are invalid or the user does not have enough permissions.
    """
    try:
        user = await get_user(token=token)

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
    security_scopes: _SecurityScopes,
    api_key: _Annotated[
        str,
        _Depends(API_KEY_HEADER),
    ],
) -> _UserShortSchema:
    """
    Retrieves a user from the API key and performs permission checks.

    Args:
        security_scopes (SecurityScopes): The security scopes required for the endpoint.
        api_key (str): The API key provided in the request header.

    Returns:
        UserShortSchema: The user associated with the API key.

    Raises:
        HTTPException: If the API key is invalid or the user does not have sufficient permissions.
    """
    try:
        if api_key is None:
            raise _InvalidCredentialsError()

        user = await get_api_key(api_key=api_key)

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
