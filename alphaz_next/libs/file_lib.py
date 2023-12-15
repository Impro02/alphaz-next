# MODULES
import json
import os
from pathlib import Path


def open_json_file(path: Path, encoding="utf-8"):
    if not os.path.exists(path):
        raise FileExistsError(f"File {path} does not exist")

    with open(path, encoding=encoding) as json_file:
        raw_data: dict = json.load(json_file)

    return raw_data
