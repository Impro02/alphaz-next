# MODULES
import json
from pathlib import Path
from typing import Any, Dict, List, Union


def open_json_file(path: Path, encoding="utf-8"):
    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist")

    if not path.is_file():
        raise FileExistsError(f"Path {path} is not a file")

    with open(path, encoding=encoding) as json_file:
        raw_data: Union[List[Dict], Dict] = json.load(json_file)

    return raw_data


def save_json_file(
    path: Path,
    data: Any,
    encoding: str = "utf-8",
):
    if path.exists():
        return

    with open(path, "w", encoding=encoding) as file:
        file.write(json.dumps(data))


def save_file(
    path: Path,
    data: bytes,
    encoding: str = "utf-8",
    new_line: str = "\n",
):
    if path.exists():
        return

    text_data = data.decode(encoding)

    with open(path, "w", encoding=encoding, newline=new_line) as file:
        file.write(text_data)
