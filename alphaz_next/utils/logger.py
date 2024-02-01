# MODULES
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# UTILS
from alphaz_next.utils.logging_filters import (
    LevelFilter,
    AttributeFilter,
)

DEFAULT_FORMAT = "%(asctime)s - %(levelname)-7s - %(process)5d - %(module)+15s.%(lineno)-4d - %(name)-14s: %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class AlphaLogger:
    def __init__(
        self,
        name: str,
        directory: str,
        level: int = logging.INFO,
        stream_output: bool = True,
        when: str = "midnight",
        interval: int = 1,
        backup_count: int = 10,
        file_name: Optional[str] = None,
        logging_formatter: str = DEFAULT_FORMAT,
        date_formatter: str = DEFAULT_DATE_FORMAT,
    ):
        self._name = name

        if file_name is None:
            file_name = name

        directory_path = Path(directory)
        directory_path.mkdir(parents=True, exist_ok=True)

        logger_config = {
            "level": level,
            "directory_path": directory_path,
            "when": when,
            "interval": interval,
            "backup_count": backup_count,
            "logging_formatter": logging_formatter,
            "date_formatter": date_formatter,
        }

        self._logger = self._create_logger(
            name=name,
            file_name=file_name,
            stream_output=stream_output,
            **logger_config,
        )

    def info(
        self,
        message: str,
        exc_info: Exception = None,
        stack_level: int = 1,
        monitor: Optional[str] = None,
    ):
        self._logger.info(
            message,
            exc_info=exc_info,
            stacklevel=stack_level + 1,
            extra={
                "monitor": monitor,
            },
        )

    def warning(
        self,
        message: str,
        exc_info: Exception = None,
        stack_level: int = 1,
        monitor: Optional[str] = None,
    ):
        self._logger.warning(
            message,
            exc_info=exc_info,
            stacklevel=stack_level + 1,
            extra={
                "monitor": monitor,
            },
        )

    def error(
        self,
        message: str,
        exc_info: Exception = None,
        stack_level: int = 1,
        monitor: Optional[str] = None,
    ):
        self._logger.error(
            message,
            exc_info=exc_info,
            stacklevel=stack_level + 1,
            extra={
                "monitor": monitor,
            },
        )

    def critical(
        self,
        message: str,
        exc_info: Exception = None,
        stack_level: int = 1,
        monitor: Optional[str] = None,
    ):
        self._logger.critical(
            message,
            exc_info=exc_info,
            stacklevel=stack_level + 1,
            extra={
                "monitor": monitor,
            },
        )

    def _create_logger(
        self,
        name: str,
        level: int,
        directory_path: Path,
        file_name: str,
        when: str,
        interval: int,
        backup_count: int,
        logging_formatter: str,
        date_formatter: str,
        stream_output: bool = False,
    ):
        logger = logging.getLogger(name=name)
        logger.propagate = False

        if logger.hasHandlers():
            return logger

        formatter = logging.Formatter(
            logging_formatter,
            datefmt=date_formatter,
        )

        monitoring_formatter = logging.Formatter(
            f"[%(monitor)s] ({logging_formatter})",
            datefmt=date_formatter,
        )

        logger.setLevel(level)

        if stream_output:
            # Add a stream handler to log messages to stdout
            stream_handler = logging.StreamHandler(stream=sys.stdout)
            stream_handler.setLevel(level)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        # Add a file handler to log messages to a file
        time_rotating_handler = self._create_time_rotating_handler(
            file_path=directory_path / f"{file_name}.log",
            level=level,
            formatter=formatter,
            when=when,
            interval=interval,
            backup_count=backup_count,
        )

        # Add a warning file handler to log warning messages to a file
        warning_time_rotating_handler = self._create_time_rotating_handler(
            file_path=directory_path / "warnings.log",
            level=level,
            formatter=formatter,
            when=when,
            interval=interval,
            backup_count=backup_count,
            filter=LevelFilter,
            filter_kwargs={
                "levels": [logging.WARNING],
            },
        )

        # Add a error file handler to log error messages to a file
        error_time_rotating_handler = self._create_time_rotating_handler(
            file_path=directory_path / "errors.log",
            level=level,
            formatter=formatter,
            when=when,
            interval=interval,
            backup_count=backup_count,
            filter=LevelFilter,
            filter_kwargs={
                "levels": [logging.ERROR, logging.CRITICAL],
            },
        )

        # Add a monitoring file handler to log messages linked to a monitor to a file
        monitoring_time_rotating_handler = self._create_time_rotating_handler(
            file_path=directory_path / "monitoring.log",
            level=level,
            formatter=monitoring_formatter,
            when=when,
            interval=interval,
            backup_count=backup_count,
            filter=AttributeFilter,
            filter_kwargs={
                "param": "monitor",
            },
        )

        logger.addHandler(time_rotating_handler)
        logger.addHandler(warning_time_rotating_handler)
        logger.addHandler(error_time_rotating_handler)
        logger.addHandler(monitoring_time_rotating_handler)

        return logger

    def _create_time_rotating_handler(
        self,
        file_path: Path,
        level: int,
        formatter: logging.Formatter,
        when: str,
        interval: int,
        backup_count: int,
        filter: Optional[Callable[..., logging.Filter]] = None,
        filter_kwargs: Optional[Dict[str, Any]] = None,
    ):
        handler = TimedRotatingFileHandler(
            filename=file_path,
            when=when,
            interval=interval,
            backupCount=backup_count,
        )
        handler.setLevel(level)
        handler.setFormatter(formatter)

        if filter is not None:
            handler.addFilter(filter(**filter_kwargs or {}))

        return handler
