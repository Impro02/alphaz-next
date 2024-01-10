# MODULES
from pathlib import Path
from typing import Dict, Optional, Type, TypeVar, Union
import warnings

# PYDANTIC
from pydantic import BaseModel, ConfigDict, Field, computed_field

# LIBS
from alphaz_next.libs.file_lib import open_json_file

# MODELS
from alphaz_next.models.config.alpha_config import (
    ReservedConfigItem,
    replace_reserved_config,
)


class AlphaDatabaseConfigSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ini: bool = False
    init_database_dir_json: Optional[str] = Field(default=None)
    connect_args: Optional[Dict] = Field(default=None)

    @computed_field
    @property
    def connection_string(self) -> str:
        raise NotImplementedError()


class AlphaDatabaseOracleConfigSchema(AlphaDatabaseConfigSchema):
    host: str
    username: str
    password: str
    port: int
    service_name: str
    type: str

    @computed_field
    @property
    def connection_string(self) -> str:
        return (
            f"oracle+cx_oracle://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.service_name}"
        )


class AlphaDatabaseSqliteConfigSchema(AlphaDatabaseConfigSchema):
    path: str

    @computed_field
    @property
    def connection_string(self) -> str:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{self.path}"


_T = TypeVar("_T", bound=BaseModel)


def create_databases_config(
    model: Type[_T],
    databases_config_path: Path,
    reserved_config: ReservedConfigItem,
) -> Optional[_T]:
    data = open_json_file(path=databases_config_path)

    configs: Dict[
        str : Union[AlphaDatabaseOracleConfigSchema, AlphaDatabaseOracleConfigSchema]
    ] = {}
    for k, v in data.items():
        db_type = v.get("type")
        v = replace_reserved_config(
            v,
            reserved_config=reserved_config,
        )
        match db_type:
            case "oracle":
                configs[k] = AlphaDatabaseOracleConfigSchema.model_validate(v)
            case "sqlite":
                configs[k] = AlphaDatabaseSqliteConfigSchema.model_validate(v)
            case _:
                warnings.warn(f"database type {db_type} is not supported")

    return model.model_validate(configs)
