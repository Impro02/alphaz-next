# MODULES
from datetime import datetime
from typing import List, Optional

# PYDANTIC
from pydantic import BaseModel, Field


class UserShortSchema(BaseModel):
    """
    Represents a short schema for a user.

    Attributes:
        username (str): The username of the user.
        last_activity (datetime): The last activity timestamp of the user.
        permissions (List[str], optional): The list of permissions for the user. Defaults to an empty list.
    """

    username: str
    last_activity: datetime
    permissions: List[str] = Field(default_factory=lambda: [])


class UserSchema(UserShortSchema):
    """
    Represents a user with additional information.

    Attributes:
        id (int): The user's ID.
        registered_date (datetime): The date when the user registered.
        email (Optional[str], optional): The user's email address. Defaults to None.
        short_login (Optional[str], optional): The user's short login. Defaults to None.
        full_name (Optional[str], optional): The user's full name. Defaults to None.
        location (Optional[str], optional): The user's location. Defaults to None.
        country (Optional[str], optional): The user's country. Defaults to None.
        region (Optional[str], optional): The user's region. Defaults to None.
        disabled (bool): Indicates if the user is disabled.
    """

    id: int
    registered_date: datetime
    email: Optional[str] = Field(default=None)
    short_login: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None)
    region: Optional[str] = Field(default=None)
    disabled: bool
