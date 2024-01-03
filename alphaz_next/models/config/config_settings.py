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
    config_dir_alias: str = "ALPHA_CONFIG_DIR",
):
    class AlphaConfigSettingsSchema(BaseSettings):
        environment: str = Field(validation_alias=environment_alias)
        config_dir: str = Field(validation_alias=config_dir_alias)

        @computed_field
        @property
        def main_config(self) -> _T:
            config_file_path = Path(self.config_dir) / f"config.{self.environment}.json"

            data = open_json_file(path=config_file_path)

            data_ext = {
                "environment": self.environment,
                "config_file_path": config_file_path,
            }

            data.update(data_ext)

            return model.model_validate(data)

    return AlphaConfigSettingsSchema().main_config
