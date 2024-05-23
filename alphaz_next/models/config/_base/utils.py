# MODULES
import getpass
import os
import re
from typing import Any, Dict, List, TypeVar, TypedDict, Union, cast
from pathlib import Path

# LIBS
from alphaz_next.libs.file_lib import open_json_file


_CONFIG_PATTERN = r"\$config\(([^)]*)\)"

_T = TypeVar("_T", bound=Union[List[Dict[str, Any]], Dict[str, Any]])


class ReservedConfigItem(TypedDict):
    """
    Represents a reserved configuration item.

    Attributes:
        environment (str): The environment.
        root (str): The root directory.
        project_name (str): The project name.
    """

    environment: str
    root: str
    project_name: str


def replace_reserved_config(
    config: _T,
    reserved_config: ReservedConfigItem,
) -> _T:
    """
    Replaces reserved variables in the configuration dictionary with their corresponding values.

    Args:
        config (Dict): The original configuration dictionary.
        reserved_config (ReservedConfigItem): The reserved configuration item containing the values for the reserved variables.

    Returns:
        Dict: The updated configuration dictionary with the reserved variables replaced.
    """
    replaced_config = config.copy()

    def open_child_config(value: Any) -> Any:
        if not isinstance(value, str):
            return value

        match = re.search(_CONFIG_PATTERN, value)

        if not match:
            return value

        result = match.group(1)

        result = open_json_file(Path(result))

        return traverse(result)

    def replace_variable(value: Any) -> Any:
        if not isinstance(value, str):
            return value

        return (
            value.replace("{{root}}", reserved_config["root"])
            .replace("{{project_name}}", reserved_config["project_name"])
            .replace("{{environment}}", reserved_config["environment"])
            .replace("{{home}}", os.path.expanduser("~"))
            .replace("{{user}}", getpass.getuser())
            .replace("{{project}}", os.path.abspath(os.getcwd()))
        )

    def traverse(
        obj: Union[List[Dict[str, Any]], Dict[str, Any]]
    ) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
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

    return cast(_T, traverse(replaced_config))
