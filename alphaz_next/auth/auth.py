# MODULES
import json
from typing import Annotated, List

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


def decode_token(token: str):
    try:
        return jwt.decode(
            token,
            INTERNAL_CONFIG.secret_key,
            algorithms=[INTERNAL_CONFIG.algorithm],
        )
    except JWTError:
        raise InvalidCredentialsError()


async def get_user(token: str):
    payload = decode_token(token=token)

    username: str = payload.get("sub")
    if username is None:
        raise InvalidCredentialsError()

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


async def get_user_from_jwt(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
) -> UserSchema:
    permissions = security_scopes.scopes
    try:
        user = await get_user(token=token)

        if len(permissions) > 0 and not any(
            [user_permission in permissions for user_permission in user.permissions]
        ):
            raise NotEnoughPermissionsError()

    except InvalidCredentialsError as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=json.dumps(ex.args),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except NotEnoughPermissionsError as ex:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=json.dumps(ex.args),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_user_from_api_key(
    api_key: Annotated[
        str,
        Depends(API_KEY_HEADER),
    ],
) -> UserShortSchema:
    try:
        if api_key is None:
            raise InvalidCredentialsError()

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
    except InvalidCredentialsError as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=json.dumps(ex.args),
            headers={"WWW-Authenticate": "Bearer"},
        )
