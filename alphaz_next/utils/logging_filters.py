# MODULES
import logging
import re
from typing import List


class LevelFilter(logging.Filter):
    def __init__(self, levels: List[int]) -> None:
        super().__init__()
        self._levels = levels

    def filter(self, record):
        return record.levelno in self._levels


class AttributeFilter(logging.Filter):
    def __init__(self, param: str) -> None:
        super().__init__()
        self.param_ = param

    def filter(self, record):
        monitor = record.__dict__.get(self.param_, None)
        return monitor is not None


class ExcludeRoutersFilter(logging.Filter):
    def __init__(self, router_names: List[str], pattern: str = r'"([A-Z]+) ([^"]+)"'):
        super().__init__()
        self.router_names = router_names
        self._pattern = pattern

    def filter(self, record):
        match = re.search(self._pattern, record.getMessage())
        if match and match.group(2) in self.router_names:
            return False

        return True
