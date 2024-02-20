# PYDANTIC
from pydantic import BaseModel, ConfigDict


class DirectoriesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    logs: str
