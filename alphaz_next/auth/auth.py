# MODULES
from typing import Annotated, Any, Dict, List

# FASTAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer, SecurityScopes

# JOSE
from jose import JWTError, jwt

# LIBS
from alphaz_next.libs.httpx import (
    make_async_request_with_retry,
    post_process_http_response,
)

# MODELS
from alphaz_next.models.auth.user import UserSchema, UserShortSchema
from alphaz_next.models.config._base.internal_config_settings import (
    create_internal_config,
)

# EXCEPTIONS
from alphaz_next.core.exception import (
    InvalidCredentialsError,
    NotEnoughPermissionsError,
)

INTERNAL_CONFIG = create_internal_config()

API_KEY_HEADER = APIKeyHeader(name="api_key", auto_error=False)
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl=INTERNAL_CONFIG.token_url)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            INTERNAL_CONFIG.secret_key,
            algorithms=[INTERNAL_CONFIG.algorithm],
        )
    except JWTError:
        raise InvalidCredentialsError()

    username: str = payload.get("sub")
    if username is None:
        raise InvalidCredentialsError()

    return payload


async def get_user(token: str) -> UserSchema:
    decode_token(token=token)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = await make_async_request_with_retry(
        method="POST",
        url=INTERNAL_CONFIG.user_me_url,
        **{
            "headers": headers,
        },
    )

    return post_process_http_response(
        response,
        schema=UserSchema,
    )


async def get_api_key(api_key: str) -> UserShortSchema:
    headers = {
        "api_key": api_key,
    }

    response = await make_async_request_with_retry(
        method="POST",
        url=INTERNAL_CONFIG.api_key_me_url,
        **{
            "headers": headers,
        },
    )

    return post_process_http_response(
        response,
        schema=UserShortSchema,
    )


def check_user_permissions(permissions: List[str], user_permissions: List[str]) -> None:
    if len(permissions) > 0 and not any(
        [user_permission in permissions for user_permission in user_permissions]
    ):
        raise NotEnoughPermissionsError()


async def get_user_from_jwt(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
) -> UserSchema:
    try:
        user = await get_user(token=token)

        check_user_permissions(
            permissions=security_scopes.scopes,
            user_permissions=user.permissions,
        )

        return user

    except InvalidCredentialsError as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ex.args[0],
            headers={"WWW-Authenticate": "Bearer"},
        )
    except NotEnoughPermissionsError as ex:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ex.args[0],
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_user_from_api_key(
    security_scopes: SecurityScopes,
    api_key: Annotated[
        str,
        Depends(API_KEY_HEADER),
    ],
) -> UserShortSchema:
    try:
        if api_key is None:
            raise InvalidCredentialsError()

        user = await get_api_key(api_key=api_key)

        check_user_permissions(
            permissions=security_scopes.scopes,
            user_permissions=user.permissions,
        )

        return user

    except InvalidCredentialsError as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ex.args[0],
            headers={"WWW-Authenticate": "Bearer"},
        )
    except NotEnoughPermissionsError as ex:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ex.args[0],
            headers={"WWW-Authenticate": "Bearer"},
        )
