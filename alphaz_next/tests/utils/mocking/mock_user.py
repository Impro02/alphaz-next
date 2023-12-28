# MODULES
from datetime import datetime
from typing import List, Optional

# MODELS
from alphaz_next.models.auth.user import UserSchema, UserShortSchema

GET_USER_PATH = "alphaz_next.auth.auth.get_user"
GET_API_KEY_PATH = "alphaz_next.auth.auth.get_api_key"


def get_mocked_user(
    id: int = 1,
    username: str = "foo",
    email: Optional[str] = "foo@st.com",
    short_login: Optional[str] = "bar",
    full_name: Optional[str] = "zoo",
    location: Optional[str] = None,
    country: Optional[str] = None,
    region: Optional[str] = None,
    disabled: bool = False,
    registered_date: datetime = datetime.now(),
    last_activity: datetime = datetime.now(),
    permissions: List[str] = [],
):
    return UserSchema(
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
    last_activity: datetime = datetime.now(),
    permissions: List[str] = [],
) -> UserShortSchema:
    return UserShortSchema(
        username=username,
        last_activity=last_activity,
        permissions=permissions,
    )
