# MODULES
from pathlib import Path as _Path
from typing import (
    Dict as _Dict,
    Optional as _Optional,
    Type as _Type,
    TypeVar as _TypeVar,
)
import warnings as _warnings

# PYDANTIC
from pydantic import (
    BaseModel as _BaseModel,
    ConfigDict as _ConfigDict,
    Field as _Field,
    computed_field as _computed_field,
)

# LIBS
from alphaz_next.libs.file_lib import open_json_file as _open_json_file
from alphaz_next.models.config._base.utils import (
    ReservedConfigItem as _ReservedConfigItem,
    replace_reserved_config as _replace_reserved_config,
)


class AlphaDatabaseConfigSchema(_BaseModel):
    """
    Represents the configuration schema for the Alpha Database.
    """

    model_config = _ConfigDict(from_attributes=True)

    ini: bool = False
    init_database_dir_json: _Optional[str] = _Field(default=None)
    connect_args: _Optional[_Dict] = _Field(default=None)
    create_on_start: bool = False

    @_computed_field
    @property
    def connection_string(self) -> str:
        raise NotImplementedError()


class _AlphaDatabaseOracleConfigSchema(AlphaDatabaseConfigSchema):
    """
    Represents the configuration schema for an Oracle database connection using cx_oracle driver.
    """

    host: str
    username: str
    password: str
    port: int
    service_name: str
    type: str

    @_computed_field
    @property
    def connection_string(self) -> str:
        """
        Returns the connection string for the Oracle database.
        """
        return (
            f"oracle+cx_oracle://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.service_name}"
        )


class _AlphaDatabaseOracleDbConfigSchema(AlphaDatabaseConfigSchema):
    """
    Represents the configuration schema for an Oracle database connection using oracledb driver.
    """

    host: str
    username: str
    password: str
    port: int
    service_name: str
    type: str

    @_computed_field
    @property
    def connection_string(self) -> str:
        """
        Returns the connection string for the Oracle database.
        """
        return (
            f"oracle+oracledb://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.service_name}"
        )


class _AlphaDatabaseOracleDbAsyncConfigSchema(AlphaDatabaseConfigSchema):
    """
    Represents the configuration schema for an Oracle database connection using oracledb_async driver.
    """

    host: str
    username: str
    password: str
    port: int
    service_name: str
    type: str

    @_computed_field
    @property
    def connection_string(self) -> str:
        """
        Returns the connection string for the Oracle database.
        """
        return (
            f"oracle+oracledb_async://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.service_name}"
        )


class _AlphaDatabaseSqliteConfigSchema(AlphaDatabaseConfigSchema):
    """
    Represents the configuration schema for an SQLite database connection.
    """

    path: str

    @_computed_field
    @property
    def connection_string(self) -> str:
        """
        Returns the connection string for the SQLite database.
        Creates the parent directory if it doesn't exist.
        """
        _Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{self.path}"


class _AlphaDatabaseAioSqliteConfigSchema(AlphaDatabaseConfigSchema):
    """
    Represents the configuration schema for an SQLite database connection using aiosqlite driver.
    """

    path: str

    @_computed_field
    @property
    def connection_string(self) -> str:
        """
        Returns the connection string for the SQLite database.
        """
        _Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite+aiosqlite:///{self.path}"


_T = _TypeVar("_T", bound=_BaseModel)


def create_databases_config(
    model: _Type[_T],
    databases_config_path: _Path,
    reserved_config: _ReservedConfigItem,
) -> _Optional[_T]:
    data = _open_json_file(path=databases_config_path)

    configs = {}
    for k, v in data.items():
        db_type = v.get("type")
        v = _replace_reserved_config(
            v,
            reserved_config=reserved_config,
        )
        match db_type:
            case "oracle":
                configs[k] = _AlphaDatabaseOracleConfigSchema.model_validate(v)
            case "oracledb":
                configs[k] = _AlphaDatabaseOracleDbConfigSchema.model_validate(v)
            case "oracledb_async":
                configs[k] = _AlphaDatabaseOracleDbAsyncConfigSchema.model_validate(v)
            case "sqlite":
                configs[k] = _AlphaDatabaseSqliteConfigSchema.model_validate(v)
            case "aiosqlite":
                configs[k] = _AlphaDatabaseAioSqliteConfigSchema.model_validate(v)
            case _:
                _warnings.warn(f"database type {db_type} is not supported")

    return model.model_validate(configs)
