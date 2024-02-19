# MODULES
from pathlib import Path as _Path
from typing import (
    Dict as _Dict,
    Optional as _Optional,
)

# PYDANTIC
from pydantic import (
    BaseModel as _BaseModel,
    ConfigDict as _ConfigDict,
    Field as _Field,
    computed_field as _computed_field,
    model_validator as _model_validator,
)


class _DatabaseConfigBaseSchema(_BaseModel):
    """
    Represents the configuration schema for the Database.
    """

    model_config = _ConfigDict(from_attributes=True)

    driver: str
    ini: bool = False
    init_database_dir_json: _Optional[str] = _Field(default=None)
    connect_args: _Optional[_Dict] = _Field(default=None)


class _DatabaseCxOracleConfigSchema(_DatabaseConfigBaseSchema):
    """
    Represents the configuration schema for an Oracle database connection using cx_oracle driver.
    """

    host: str
    username: str
    password: str
    port: int
    service_name: str

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


class _DatabaseOracleDbConfigSchema(_DatabaseConfigBaseSchema):
    """
    Represents the configuration schema for an Oracle database connection using oracledb driver.
    """

    host: str
    username: str
    password: str
    port: int
    service_name: str

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


class _DatabaseOracleDbAsyncConfigSchema(_DatabaseConfigBaseSchema):
    """
    Represents the configuration schema for an Oracle database connection using oracledb_async driver.
    """

    host: str
    username: str
    password: str
    port: int
    service_name: str

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


class _DatabaseSqliteConfigSchema(_DatabaseConfigBaseSchema):
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


class _DatabaseAioSqliteConfigSchema(_DatabaseConfigBaseSchema):
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


class DatabaseConfigSchema(_BaseModel):
    """
    Represents the configuration schema for the Database.
    """

    model_config = _ConfigDict(from_attributes=True)

    connection_string: str
    ini: bool = False
    init_database_dir_json: _Optional[str] = _Field(default=None)
    connect_args: _Optional[_Dict] = _Field(default=None)


class DatabasesConfigSchema(_BaseModel):
    """
    Represents the configuration schema for the Databases.
    """

    model_config = _ConfigDict(from_attributes=True)

    databases: _Dict[
        str,
        DatabaseConfigSchema,
    ]

    @_model_validator(mode="before")
    @classmethod
    def validate_config(cls, data: _Dict) -> _Dict:
        data_tmp = {}
        for k, v in data.items():
            if "driver" not in v:
                raise AttributeError("driver must be assigned in db config file")

            match (driver := v.get("driver")):
                case "cx_oracle":
                    config = _DatabaseCxOracleConfigSchema(**v)
                    data_tmp[k] = config.model_dump()
                case "oracledb":
                    config = _DatabaseOracleDbConfigSchema(**v)
                    data_tmp[k] = config.model_dump()
                case "oracledb_async":
                    config = _DatabaseOracleDbAsyncConfigSchema(**v)
                    data_tmp[k] = config.model_dump()
                case "sqlite":
                    config = _DatabaseSqliteConfigSchema(**v)
                    data_tmp[k] = config.model_dump()
                case "aiosqlite":
                    config = _DatabaseAioSqliteConfigSchema(**v)
                    data_tmp[k] = config.model_dump()
                case _:
                    raise RuntimeError(f"database type {driver=} is not supported")

        return {"databases": data_tmp}
