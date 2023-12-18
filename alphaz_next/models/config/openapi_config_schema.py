# MODULES
from typing import Optional

# PYDANTIC
from pydantic import BaseModel, ConfigDict, Field


class ContactSchema(BaseModel):
    name: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)


class OpenApiSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    description: Optional[str] = Field(default=None)
    contact: Optional[ContactSchema] = Field(default=None)
