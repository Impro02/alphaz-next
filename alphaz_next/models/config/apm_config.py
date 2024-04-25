# MODULES
from typing import Optional as _Optional

# PYDANTIC
from pydantic import (
    BaseModel as _BaseModel,
    ConfigDict as _ConfigDict,
    Field as _Field,
)


class ApmConfig(_BaseModel):
    """
    Configuration class for APM (Application Performance Monitoring).
    """

    model_config = _ConfigDict(from_attributes=True)

    server_url: str
    certificate_file: _Optional[str] = _Field(default=None)
    ssl_verify: bool = _Field(default=True)
    debug: bool = _Field(default=True)
    active: bool = _Field(default=False)
