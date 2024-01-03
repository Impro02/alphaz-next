# MODULES
import getpass
import os
from typing import Any, Dict, TypedDict
from pathlib import Path

# PYDANTIC
from pydantic import BaseModel, ConfigDict, model_validator


class ReservedConfigItem(TypedDict):
    root: str
    project_name: str


class AlphaConfigSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    environment: str
    config_file_path: Path
    project_name: str
    version: str
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
