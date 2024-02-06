# MODULES
from pathlib import Path as _Path
from typing import Type as _Type, TypeVar as _TypeVar

# PYDANTIC
from pydantic import Field as _Field, computed_field as _computed_field
from pydantic_settings import BaseSettings as _BaseSettings

# LIBS
from alphaz_next.libs.file_lib import open_json_file as _open_json_file
from alphaz_next.models.config.alpha_config import (
    AlphaConfigSchema as _AlphaConfigSchema,
)

_T = _TypeVar("_T", bound=_AlphaConfigSchema)


def create_config_settings(
    path: _Path,
    model: _Type[_T],
    environment_alias: str = "ALPHA_ENV",
    root_alias: str = "ALPHA_ROOT",
    port_alias: str = "ALPHA_PORT",
    workers_alias: str = "ALPHA_WORKERS",
):
    """
    Create configuration settings based on the provided parameters.

    Args:
        path (Path): The path to the JSON file containing the configuration data.
        model (Type[_T]): The model class used for validating the configuration data.
        environment_alias (str, optional): The alias for the environment field in the JSON file. Defaults to "ALPHA_ENV".
        root_alias (str, optional): The alias for the root field in the JSON file. Defaults to "ALPHA_ROOT".
        port_alias (str, optional): The alias for the port field in the JSON file. Defaults to "ALPHA_PORT".
        workers_alias (str, optional): The alias for the workers field in the JSON file. Defaults to "ALPHA_WORKERS".

    Returns:
        _T: The validated configuration data based on the provided model class.
    """

    class AlphaConfigSettingsSchema(_BaseSettings):
        environment: str = _Field(validation_alias=environment_alias)
        root: str = _Field(validation_alias=root_alias)
        port: int = _Field(validation_alias=port_alias)
        workers: int = _Field(validation_alias=workers_alias)

        @_computed_field
        @property
        def main_config(self) -> _T:
            data = _open_json_file(path=_Path(path))

            data_ext = {
                "environment": self.environment,
                "root": self.root,
                "port": self.port,
                "workers": self.workers,
            }

            data.update(data_ext)

            return model.model_validate(data)

    return AlphaConfigSettingsSchema().main_config
