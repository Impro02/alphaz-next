# MODULES
from typing import Dict as _Dict, List as _List, Optional as _Optional

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
    configuration: _Optional[_Dict[str, _Optional[_List[str]]]] = _Field(default=None)
