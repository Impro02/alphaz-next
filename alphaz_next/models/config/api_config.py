# MODULES
from typing import Optional

# PYDANTIC
from pydantic import BaseModel, ConfigDict, Field

# MODELS
from alphaz_next.models.config.apm_config import ApmConfig


class ApiConfigSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="allow",
    )

    databases_config_path: str
    port: int
    workers: int
    apm: Optional[ApmConfig] = Field(default=None)
