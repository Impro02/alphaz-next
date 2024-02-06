# MODULES
from datetime import datetime as _datetime
from typing import List as _List, Optional as _Optional

# MODELS
from alphaz_next.models.auth.user import (
    UserSchema as _UserSchema,
    UserShortSchema as _UserShortSchema,
)

GET_USER_PATH = "alphaz_next.auth.auth.get_user"
GET_API_KEY_PATH = "alphaz_next.auth.auth.get_api_key"


def get_mocked_user(
    id: int = 1,
    username: str = "foo",
    email: _Optional[str] = "foo@st.com",
    short_login: _Optional[str] = "bar",
    full_name: _Optional[str] = "zoo",
    location: _Optional[str] = None,
    country: _Optional[str] = None,
    region: _Optional[str] = None,
    disabled: bool = False,
    registered_date: _datetime = _datetime.now(),
    last_activity: _datetime = _datetime.now(),
    permissions: _List[str] = [],
):
    """
    Get a mocked user object with the specified attributes.

    Args:
        id (int): The user ID.
        username (str): The username.
        email (Optional[str]): The email address. Defaults to "foo@st.com".
        short_login (Optional[str]): The short login. Defaults to "bar".
        full_name (Optional[str]): The full name. Defaults to "zoo".
        location (Optional[str]): The location.
        country (Optional[str]): The country.
        region (Optional[str]): The region.
        disabled (bool): Whether the user is disabled. Defaults to False.
        registered_date (datetime): The registered date. Defaults to the current datetime.
        last_activity (datetime): The last activity date. Defaults to the current datetime.
        permissions (List[str]): The list of permissions. Defaults to an empty list.

    Returns:
        UserSchema: The mocked user object.
    """
    return _UserSchema(
        id=id,
        username=username,
        email=email,
        short_login=short_login,
        full_name=full_name,
        location=location,
        country=country,
        region=region,
        disabled=disabled,
        registered_date=registered_date,
        last_activity=last_activity,
        permissions=permissions,
    )


def get_mocked_short_user(
    username: str = "foo",
    last_activity: _datetime = _datetime.now(),
    permissions: _List[str] = [],
) -> _UserShortSchema:
    """
    Returns a mocked UserShortSchema object with the specified username, last activity, and permissions.

    Args:
        username (str, optional): The username of the user. Defaults to "foo".
        last_activity (datetime, optional): The last activity timestamp of the user. Defaults to the current datetime.
        permissions (List[str], optional): The list of permissions for the user. Defaults to an empty list.

    Returns:
        UserShortSchema: The mocked UserShortSchema object.
    """
    return _UserShortSchema(
        username=username,
        last_activity=last_activity,
        permissions=permissions,
    )
