# MODULES
from datetime import datetime
from typing import List, Optional

# PYDANTIC
from pydantic import BaseModel, Field


class UserShortSchema(BaseModel):
    username: str
    last_activity: datetime
    permissions: List[str] = Field(default_factory=lambda: [])


class UserSchema(UserShortSchema):
    id: int
    registered_date: datetime
    email: Optional[str] = Field(default=None)
    short_login: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None)
    region: Optional[str] = Field(default=None)
    disabled: bool
