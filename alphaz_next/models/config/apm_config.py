# MODULES
from typing import Optional

# PYDANTIC
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ApmConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    server_url: Optional[str] = Field(default=None)
    environment: Optional[str] = Field(default=None)
    ssl_ca_cert: Optional[str] = Field(default=None)
    ssl_verify: bool = Field(default=True)
    debug: bool = Field(default=True)
    active: bool = Field(default=False)

    @model_validator(mode="after")
    def validate_model(self):
        if not self.active:
            return self

        if self.server_url is None:
            raise ValueError(f"server_url cannot be None if {self.active=}")

        if self.environment is None:
            raise ValueError(f"environment cannot be None if {self.active=}")

        return self
