# MODULES
import getpass
import os
import re
from typing import Any, Dict, TypedDict
from pathlib import Path

# PYDANTIC
from pydantic import BaseModel, ConfigDict, model_validator

# LIBS
from alphaz_next.libs.file_lib import open_json_file

# MODELS
from alphaz_next.models.config.api_config import AlphaApiConfigSchema

_CONFIG_PATTERN = r"\$config\(([^)]*)\)"


class ReservedConfigItem(TypedDict):
    environment: str
    root: str
    project_name: str


class AlphaConfigSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    environment: str
    project_name: str
    version: str
    root: str
    port: int
    workers: int

    api_config: AlphaApiConfigSchema

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, data: Dict[str, Any]) -> Dict:
        tmp = replace_reserved_config(
            data,
            reserved_config=ReservedConfigItem(
                environment=data.get("environment"),
                root=data.get("root"),
                project_name=data.get("project_name"),
            ),
        )

        reserved_fields = ReservedConfigItem(
            environment=data.get("environment"),
            root=tmp.get("root"),
            project_name=tmp.get("project_name"),
        )

        for key, value in tmp.items():
            if isinstance(value, dict):
                tmp[key]["__reserved_fields__"] = reserved_fields

        return tmp


def replace_reserved_config(
    config: Dict,
    reserved_config: ReservedConfigItem,
) -> Dict:
    replaced_config = config.copy()

    def open_child_config(value: str):
        if not isinstance(value, str):
            return value

        match = re.search(_CONFIG_PATTERN, value)

        if not match:
            return value

        result = match.group(1)

        result = open_json_file(Path(result))

        return traverse(result)

    def replace_variable(value: Any):
        return (
            (
                value.replace("{{root}}", reserved_config.get("root"))
                .replace("{{home}}", os.path.expanduser("~"))
                .replace("{{project_name}}", reserved_config.get("project_name"))
                .replace("{{user}}", getpass.getuser())
                .replace("{{project}}", os.path.abspath(os.getcwd()))
                .replace("{{environment}}", reserved_config.get("environment"))
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
                    replaced_variable = replace_variable(value)
                    obj[key] = open_child_config(replaced_variable)
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                if isinstance(value, (dict, list)):
                    traverse(value)
                else:
                    replaced_variable = replace_variable(value)
                    obj[i] = open_child_config(replaced_variable)

        return obj

    return traverse(replaced_config)
