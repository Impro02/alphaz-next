# MODULES
from typing import Optional

# PYDANTIC
from pydantic import BaseModel, ConfigDict, Field

# MODELS
from alphaz_next.models.config.apm_config import ApmConfig
from alphaz_next.models.config.logging_config import LoggingSchema
from alphaz_next.models.config.openapi_config_schema import OpenApiSchema


class AlphaApiConfigSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="allow",
    )

    databases_config_path: str
    port: int
    workers: int
    logging: LoggingSchema
    apm: Optional[ApmConfig] = Field(default=None)
    openapi: Optional[OpenApiSchema] = Field(default=None)
