# MODULES
from typing import Optional as _Optional

# PYDANTIC
from pydantic import (
    BaseModel as _BaseModel,
    ConfigDict as _ConfigDict,
    Field as _Field,
    model_validator as _model_validator,
)


class ApmConfig(_BaseModel):
    """
    Configuration class for APM (Application Performance Monitoring).
    """

    model_config = _ConfigDict(from_attributes=True)

    server_url: _Optional[str] = _Field(default=None)
    environment: _Optional[str] = _Field(default=None)
    ssl_ca_cert: _Optional[str] = _Field(default=None)
    ssl_verify: bool = _Field(default=True)
    debug: bool = _Field(default=True)
    active: bool = _Field(default=False)

    @_model_validator(mode="after")
    def validate_model(self):
        if not self.active:
            return self

        if self.server_url is None:
            raise ValueError(f"server_url cannot be None if {self.active=}")

        if self.environment is None:
            raise ValueError(f"environment cannot be None if {self.active=}")

        return self
