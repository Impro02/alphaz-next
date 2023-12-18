# MODULES
from pathlib import Path
from typing import Dict, Optional

# PYDANTIC
from pydantic import BaseModel, ConfigDict, Field, computed_field


class AlphaDatasaseConfigSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ini: bool = False
    init_database_dir_json: Optional[str] = Field(default=None)
    connect_args: Optional[Dict] = Field(default=None)

    @computed_field
    @property
    def connection_string(self) -> str:
        raise NotImplementedError()


class AlphaDatabaseOracleConfigSchema(AlphaDatasaseConfigSchema):
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


class AlphaDatabaseSqliteConfigSchema(AlphaDatasaseConfigSchema):
    path: str

    @computed_field
    @property
    def connection_string(self) -> str:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{self.path}"
