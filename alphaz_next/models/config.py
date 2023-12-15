# MODULES
import os
import getpass
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict, Union
import warnings

# PYDANTIC
from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator
from pydantic_settings import BaseSettings

# LIBS
from alphaz_next.libs.file_lib import open_json_file


class ReservedConfigItem(TypedDict):
    root: str
    project_name: str


class AlphaConfigSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_name: str
    root: str

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, data: Dict[str, Any]) -> Dict:
        tmp = replace_reserved_config(
            data,
            reserved_config=ReservedConfigItem(
                root=data.get("root"),
                project_name=data.get("project_name"),
            ),
        )

        reserved_fields = ReservedConfigItem(
            root=tmp.get("root"),
            project_name=tmp.get("project_name"),
        )

        for key, value in tmp.items():
            if isinstance(value, dict):
                tmp[key]["__reserved_fields__"] = reserved_fields

        return tmp


class AlphaConfigSettingsSchema(BaseSettings):
    node_env: str = Field(validation_alias="NODE_ENV")
    config_dir: str = Field(validation_alias="CONFIG_DIR")

    @computed_field
    @property
    def main_config(self) -> AlphaConfigSchema:
        data = open_json_file(
            path=Path(self.config_dir) / f"config.{self.node_env}.json"
        )

        return AlphaConfigSchema.model_validate(data)


def replace_reserved_config(
    config: Dict,
    reserved_config: ReservedConfigItem,
) -> Dict:
    replaced_config = config.copy()

    def replace_variable(value: Any):
        return (
            (
                value.replace("{{root}}", reserved_config.get("root"))
                .replace("{{home}}", os.path.expanduser("~"))
                .replace("{{project_name}}", reserved_config.get("project_name"))
                .replace("{{user}}", getpass.getuser())
                .replace("{{project}}", os.path.abspath(os.getcwd()))
            )
            if isinstance(value, str)
            else value
        )

    def traverse(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    traverse(value)
                else:
                    obj[key] = replace_variable(value)
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                if isinstance(value, (dict, list)):
                    traverse(value)
                else:
                    obj[i] = replace_variable(value)

        return obj

    return traverse(replaced_config)


class _AlphaDatasaseConfigSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ini: bool = False
    init_database_dir_json: Optional[str] = Field(default=None)
    connect_args: Optional[Dict] = Field(default=None)

    @computed_field
    @property
    def connection_string(self) -> str:
        raise NotImplementedError()


class _AlphaDatabaseOracleConfigSchema(_AlphaDatasaseConfigSchema):
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


class _AlphaDatabaseSqliteConfigSchema(_AlphaDatasaseConfigSchema):
    path: str

    @computed_field
    @property
    def connection_string(self) -> str:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{self.path}"


class ApmConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    server_url: Optional[str] = Field(default=None)
    debug: bool = Field(default=True)
    active: bool = Field(default=False)

    @model_validator(mode="after")
    def validate_model(self):
        if self.active and self.server_url is None:
            raise ValueError(f"server_url cannot be None if {self.active=}")

        return self


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
    def databases_config(self) -> _AlphaDatasaseConfigSchema:
        if not Path(self.databases_config_path).exists():
            return None

        data = open_json_file(path=self.databases_config_path)

        configs: Dict[
            str : Union[
                _AlphaDatabaseOracleConfigSchema, _AlphaDatabaseSqliteConfigSchema
            ]
        ] = {}
        for k, v in data.items():
            db_type = v.get("type")
            v = replace_reserved_config(
                v, reserved_config=self.model_extra.get("__reserved_fields__")
            )
            match db_type:
                case "oracle":
                    configs[k] = _AlphaDatabaseOracleConfigSchema.model_validate(v)
                case "sqlite":
                    configs[k] = _AlphaDatabaseSqliteConfigSchema.model_validate(v)
                case _:
                    warnings.warn(f"database type {db_type} is not supported")

        return _AlphaDatasaseConfigSchema.model_validate(configs)
