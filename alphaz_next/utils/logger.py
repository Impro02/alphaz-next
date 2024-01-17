# MODULES
import datetime
from enum import Enum
import os
import re
import sys
import inspect
import logging
import unidecode
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import List, Optional

DEFAULT_FORMAT = (
    "{$date} - {$level:7} - {$pid:5} - {$file:>15}.{$line:<4} - {$name:<14}: $message"
)
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class LevelEnum(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AlphaLogger:
    def __init__(
        self,
        name: str,
        directory: str,
        level: int = logging.INFO,
        when: str = "midnight",
        interval: int = 1,
        backup_count: int = 10,
        file_name: Optional[str] = None,
        logging_formatter: str = DEFAULT_FORMAT,
        date_formatter: str = DEFAULT_DATE_FORMAT,
    ):
        self._name = name
        self._logging_formatter = logging_formatter
        self._date_formatter = date_formatter
        self._date_str = None

        if file_name is None:
            file_name = name

        error_name = "errors"
        warning_name = "warnings"
        monitoring_name = "monitoring"

        directory_path = Path(directory)
        directory_path.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter()

        logger_config = {
            "level": level,
            "directory_path": directory_path,
            "when": when,
            "interval": interval,
            "backup_count": backup_count,
            "formatter": formatter,
        }

        self._logger = self._create_logger(
            name=name,
            file_name=file_name,
            stream_output=True,
            **logger_config,
        )
        self._error_logger = self._create_logger(
            name=error_name,
            file_name=error_name,
            **logger_config,
        )
        self._warning_logger = self._create_logger(
            name=warning_name,
            file_name=warning_name,
            **logger_config,
        )
        self._monitoring_logger = self._create_logger(
            name=monitoring_name,
            file_name=monitoring_name,
            **logger_config,
        )

    def info(
        self,
        message: str,
        exc_info: Exception = None,
        stack_level: int = 1,
        monitor: Optional[str] = None,
    ):
        self._log(
            level=LevelEnum.INFO,
            message=message,
            stack=inspect.stack(),
            exc_info=exc_info,
            stack_level=stack_level,
            monitor=monitor,
        )

    def warning(
        self,
        message: str,
        exc_info: Exception = None,
        stack_level: int = 1,
        monitor: Optional[str] = None,
    ):
        self._log(
            level=LevelEnum.WARNING,
            message=message,
            stack=inspect.stack(),
            exc_info=exc_info,
            stack_level=stack_level,
            monitor=monitor,
        )

    def error(
        self,
        message: str,
        exc_info: Exception = None,
        stack_level: int = 1,
        monitor: Optional[str] = None,
    ):
        self._log(
            level=LevelEnum.ERROR,
            message=message,
            stack=inspect.stack(),
            exc_info=exc_info,
            stack_level=stack_level,
            monitor=monitor,
        )

    def critical(
        self,
        message: str,
        exc_info: Exception = None,
        stack_level: int = 1,
        monitor: Optional[str] = None,
    ):
        self._log(
            level=LevelEnum.CRITICAL,
            message=message,
            stack=inspect.stack(),
            exc_info=exc_info,
            stack_level=stack_level,
            monitor=monitor,
        )

    def _log(
        self,
        level: LevelEnum,
        message: str,
        stack: List[inspect.FrameInfo],
        exc_info=None,
        stack_level: int = 1,
        monitor: Optional[str] = None,
    ):
        self._date_str = self._get_current_date()

        message_formatted = self._get_formatted_message(
            message=message,
            level=level,
            stack=stack,
            stack_level=stack_level,
        )

        match level:
            case LevelEnum.INFO:
                self._logger.info(
                    message_formatted,
                    exc_info=exc_info,
                    stacklevel=stack_level,
                )
            case LevelEnum.WARNING:
                self._logger.warning(
                    message_formatted,
                    exc_info=exc_info,
                    stacklevel=stack_level,
                )
                self._warning_logger.warning(
                    message_formatted,
                    exc_info=exc_info,
                    stacklevel=stack_level,
                )
            case LevelEnum.ERROR:
                self._logger.error(
                    message_formatted,
                    exc_info=exc_info,
                    stacklevel=stack_level,
                )
                self._error_logger.error(
                    message_formatted,
                    exc_info=exc_info,
                    stacklevel=stack_level,
                )
            case LevelEnum.CRITICAL:
                self._logger.critical(
                    message_formatted,
                    exc_info=exc_info,
                    stacklevel=stack_level,
                )
                self._error_logger.critical(
                    message_formatted,
                    exc_info=exc_info,
                    stacklevel=stack_level,
                )

        if monitor is not None:
            message_formatted = self._process_monitoring_message(
                message=message_formatted,
                monitor=monitor,
            )
            self._monitoring_logger.info(
                message_formatted,
                exc_info=exc_info,
                stacklevel=stack_level,
            )

    def _get_formatted_message(
        self,
        message: str,
        level: LevelEnum,
        stack: List[inspect.FrameInfo],
        stack_level: int = 1,
    ):
        message_formatted = self._logging_formatter

        parameters = re.findall("\{\$([a-zA-Z0-9]*):?[0-9<>]*\}", message_formatted)

        parameters_values = []

        if stack_level >= len(stack):
            stack_level = len(stack) - 1
        caller = inspect.getframeinfo(stack[stack_level][0])

        structure = "$%s"
        keys = {
            "date": self._date_str,
            "pid": os.getpid(),
            "level": level.value.upper(),
            "name": self._name,
            "path": caller.filename,
            "file": caller.filename.split(os.sep)[-1].replace(".py", ""),
            "line": caller.lineno,
        }

        for parameter_name in parameters:
            if parameter_name in keys:
                message_formatted = message_formatted.replace(
                    structure % parameter_name, ""
                )
                parameters_values.append(keys[parameter_name])

        message_formatted = message_formatted.format(*parameters_values).replace(
            structure % "message", str(message)
        )

        return message_formatted

    def _get_current_date(self):
        current_date = datetime.datetime.now()
        return current_date.strftime(self._date_formatter)

    @classmethod
    def _process_monitoring_message(cls, message: str, monitor: str) -> str:
        return unidecode.unidecode(message.replace(message, f"[{monitor}] ({message})"))

    def _create_logger(
        self,
        name: str,
        level: int,
        directory_path: Path,
        file_name: str,
        when: str,
        interval: int,
        backup_count: int,
        formatter: logging.Formatter,
        stream_output: bool = False,
    ):
        logger = logging.getLogger(name=name)

        if logger.hasHandlers():
            return logger

        logger.setLevel(level)

        if stream_output:
            # Add a stream handler to log messages to stdout
            stream_handler = logging.StreamHandler(stream=sys.stdout)
            stream_handler.setLevel(level)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        # Add a file handler to log messages to a file
        time_rotating_handler = TimedRotatingFileHandler(
            filename=directory_path / f"{file_name}.log",
            when=when,
            interval=interval,
            backupCount=backup_count,
        )
        time_rotating_handler.setLevel(level)
        time_rotating_handler.setFormatter(formatter)
        logger.addHandler(time_rotating_handler)

        return logger
