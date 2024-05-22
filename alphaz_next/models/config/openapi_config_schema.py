# MODULES
from typing import Dict as _Dict, List as _List, Optional as _Optional

# PYDANTIC
from pydantic import BaseModel as _BaseModel, ConfigDict as _ConfigDict, Field as _Field


class ContactSchema(_BaseModel):
    name: _Optional[str] = _Field(default=None)
    email: _Optional[str] = _Field(default=None)


class OpenApiSchema(_BaseModel):
    model_config = _ConfigDict(from_attributes=True)

    description: _Optional[str] = _Field(default=None)
    contact: _Optional[ContactSchema] = _Field(default=None)
    swagger_favicon_url: _Optional[str] = _Field(default=None)
    redoc_favicon_url: _Optional[str] = _Field(default=None)
    tags: _List[_Dict[str, str]] = _Field(default_factory=lambda: [])
