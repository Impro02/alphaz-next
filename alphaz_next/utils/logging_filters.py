# MODULES
import logging as _logging
import re as _re
from typing import List as _List


class LevelFilter(_logging.Filter):
    """
    A logging filter that filters log records based on their level.

    Args:
        levels (List[int]): A list of log levels to allow.

    Returns:
        bool: True if the log record's level is in the allowed levels, False otherwise.
    """

    def __init__(self, levels: _List[int]) -> None:
        super().__init__()
        self._levels = levels

    def filter(self, record):
        return record.levelno in self._levels


class AttributeFilter(_logging.Filter):
    """
    A logging filter that filters log records based on the presence of a specified attribute.

    Args:
        param (str): The name of the attribute to check for in log records.

    Returns:
        bool: True if the log record has the specified attribute, False otherwise.
    """

    def __init__(self, param: str) -> None:
        super().__init__()
        self.param_ = param

    def filter(self, record):
        monitor = record.__dict__.get(self.param_, None)
        return monitor is not None


class ExcludeRoutersFilter(_logging.Filter):
    """
    A logging filter that excludes log records based on the router names.
    """

    def __init__(
        self,
        router_names: _List[str],
        pattern: str = r'"([A-Z]+) ([^"]+)"',
    ):
        """
        Initialize the LoggingFilter object.

        Args:
            router_names (List[str]): A list of router names.
            pattern (str): A regular expression pattern used for filtering log messages.
                Defaults to r'"([A-Z]+) ([^"]+)"'.
        """
        super().__init__()
        self.router_names = router_names
        self._pattern = pattern

    def filter(self, record):
        """
        Filters the log record based on the configured pattern and router names.

        Args:
            record (LogRecord): The log record to be filtered.

        Returns:
            bool: True if the log record should be passed through the filter, False otherwise.
        """
        match = _re.search(self._pattern, record.getMessage())
        if match and match.group(2) in self.router_names:
            return False

        return True
