# PYDANTIC
from pydantic import BaseModel as _BaseModel, ConfigDict as _ConfigDict


class DirectoriesSchema(_BaseModel):
    model_config = _ConfigDict(from_attributes=True)

    logs: str
