# MODULES
import json
from pathlib import Path


def open_json_file(path: Path, encoding="utf-8"):
    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist")

    if not path.is_file():
        raise FileExistsError(f"Path {path} is not a file")

    with open(path, encoding=encoding) as json_file:
        raw_data: dict = json.load(json_file)

    return raw_data
