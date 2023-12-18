# MODULES
import os
import getpass
from pathlib import Path
from typing import Any, Dict, Type, TypeVar

# PYDANTIC
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings

# LIBS
from alphaz_next.libs.file_lib import open_json_file
from alphaz_next.models.config.alpha_config import AlphaConfigSchema, ReservedConfigItem

_T = TypeVar("_T", bound=AlphaConfigSchema)


def create_config_settings(
    model: Type[_T],
    node_env_alias: str = "NODE_ENV",
    config_dir_alias: str = "CONFIG_DIR",
):
    class AlphaConfigSettingsSchema(BaseSettings):
        node_env: str = Field(validation_alias=node_env_alias)
        config_dir: str = Field(validation_alias=config_dir_alias)

        @computed_field
        @property
        def main_config(self) -> _T:
            data = open_json_file(
                path=Path(self.config_dir) / f"config.{self.node_env}.json"
            )

            return model.model_validate(data)

    return AlphaConfigSettingsSchema()


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
