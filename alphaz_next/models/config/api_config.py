# MODULES
from typing import Optional as _Optional

# PYDANTIC
from pydantic import BaseModel as _BaseModel, ConfigDict as _ConfigDict, Field as _Field

# MODELS
from alphaz_next.models.config.apm_config import ApmConfig as _ApmConfig
from alphaz_next.models.config.logging_config import LoggingSchema as _LoggingSchema
from alphaz_next.models.config.openapi_config_schema import (
    OpenApiSchema as _OpenApiSchema,
)


class AlphaApiConfigSchema(_BaseModel):
    """
    Schema for the Alpha API configuration.
    """

    model_config = _ConfigDict(
        from_attributes=True,
        extra="allow",
    )

    databases_config_path: str
    logging: _LoggingSchema
    apm: _Optional[_ApmConfig] = _Field(default=None)
    openapi: _Optional[_OpenApiSchema] = _Field(default=None)
