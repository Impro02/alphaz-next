# MODULES
from pathlib import Path
from typing import Dict, Optional, Union
import warnings

# PYDANTIC
from pydantic import BaseModel, ConfigDict, Field, computed_field

# LIBS
from alphaz_next.libs.file_lib import open_json_file

# MODELS
from alphaz_next.models.config.alpha_config import replace_reserved_config
from alphaz_next.models.config.apm_config import ApmConfig
from alphaz_next.models.config.database_config import (
    AlphaDatabaseOracleConfigSchema,
    AlphaDatabaseSqliteConfigSchema,
    AlphaDatasaseConfigSchema,
)


class ApiConfigSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="allow",
    )

    databases_config_path: str
    port: int
    workers: int
    apm: Optional[ApmConfig] = Field(default=None)

    @computed_field
    @property
    def databases_config(self) -> AlphaDatasaseConfigSchema:
        if not Path(self.databases_config_path).exists():
            return None

        data = open_json_file(path=self.databases_config_path)

        configs: Dict[
            str : Union[
                AlphaDatabaseOracleConfigSchema, AlphaDatabaseOracleConfigSchema
            ]
        ] = {}
        for k, v in data.items():
            db_type = v.get("type")
            v = replace_reserved_config(
                v, reserved_config=self.model_extra.get("__reserved_fields__")
            )
            match db_type:
                case "oracle":
                    configs[k] = AlphaDatabaseOracleConfigSchema.model_validate(v)
                case "sqlite":
                    configs[k] = AlphaDatabaseSqliteConfigSchema.model_validate(v)
                case _:
                    warnings.warn(f"database type {db_type} is not supported")

        return AlphaDatasaseConfigSchema.model_validate(configs)
