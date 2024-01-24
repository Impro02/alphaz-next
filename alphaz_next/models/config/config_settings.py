# MODULES
from pathlib import Path
from typing import Type, TypeVar

# PYDANTIC
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings

# LIBS
from alphaz_next.libs.file_lib import open_json_file
from alphaz_next.models.config.alpha_config import AlphaConfigSchema

_T = TypeVar("_T", bound=AlphaConfigSchema)


def create_config_settings(
    model: Type[_T],
    environment_alias: str = "ALPHA_ENV",
    root_alias: str = "ALPHA_ROOT",
    config_file_path_alias: str = "ALPHA_CONFIG_FILE_PATH",
    port_alias: str = "ALPHA_PORT",
    workers_alias: str = "ALPHA_WORKERS",
):
    class AlphaConfigSettingsSchema(BaseSettings):
        environment: str = Field(validation_alias=environment_alias)
        root: str = Field(validation_alias=root_alias)
        config_file_path: str = Field(validation_alias=config_file_path_alias)
        port: int = Field(validation_alias=port_alias)
        workers: int = Field(validation_alias=workers_alias)

        @computed_field
        @property
        def main_config(self) -> _T:
            data = open_json_file(path=Path(self.config_file_path))

            data_ext = {
                "environment": self.environment,
                "root": self.root,
                "config_file_path": self.config_file_path,
                "port": self.port,
                "workers": self.workers,
            }

            data.update(data_ext)

            return model.model_validate(data)

    return AlphaConfigSettingsSchema().main_config
