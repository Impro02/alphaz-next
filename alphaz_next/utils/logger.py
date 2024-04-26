# MODULES
import sys as _sys
import logging as _logging
from logging.handlers import TimedRotatingFileHandler as _TimedRotatingFileHandler
from pathlib import Path as _Path
from typing import (
    Any as _Any,
    Callable as _Callable,
    Dict as _Dict,
    Optional as _Optional,
)

# UTILS
from alphaz_next.utils.logging_filters import (
    LevelFilter as _LevelFilter,
    AttributeFilter as _AttributeFilter,
)

DEFAULT_FORMAT = "%(asctime)s - %(levelname)-7s - %(process)5d - %(module)+15s.%(lineno)-4d - %(name)-14s: %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class Logger:
    """
    A custom logger class that provides logging functionality with various log levels and output options.
    """

    def __init__(
        self,
        name: str,
        directory: str,
        level: int = _logging.INFO,
        stream_output: bool = True,
        when: str = "midnight",
        interval: int = 1,
        backup_count: int = 10,
        file_name: _Optional[str] = None,
        logging_formatter: str = DEFAULT_FORMAT,
        date_formatter: str = DEFAULT_DATE_FORMAT,
        telemetry_handler: _Optional[_logging.Handler] = None,
    ):
        """
        Initializes a Logger object.

        Args:
            name (str): The name of the logger.
            directory (str): The directory where log files will be stored.
            level (int, optional): The logging level. Defaults to logging.INFO.
            stream_output (bool, optional): Whether to output logs to the console. Defaults to True.
            when (str, optional): The type of time-based interval for log file rotation. Defaults to "midnight".
            interval (int, optional): The interval in days for log file rotation. Defaults to 1.
            backup_count (int, optional): The number of backup log files to keep. Defaults to 10.
            file_name (str, optional): The name of the log file. If not provided, it will be the same as the logger name.
            logging_formatter (str, optional): The logging formatter string. Defaults to DEFAULT_FORMAT.
            date_formatter (str, optional): The date formatter string. Defaults to DEFAULT_DATE_FORMAT.
        """
        self._name = name

        if file_name is None:
            file_name = name

        directory_path = _Path(directory)
        directory_path.mkdir(parents=True, exist_ok=True)

        self._logger = self._create_logger(
            name=name,
            level=level,
            directory_path=directory_path,
            file_name=file_name,
            when=when,
            interval=interval,
            backup_count=backup_count,
            logging_formatter=logging_formatter,
            date_formatter=date_formatter,
            stream_output=stream_output,
            telemetry_handler=telemetry_handler,
        )

    def info(
        self,
        message: str,
        exc_info: Exception = None,
        stack_level: int = 1,
        monitor: _Optional[str] = None,
    ) -> None:
        """
        Logs an informational message.

        Args:
            message (str): The message to be logged.
            exc_info (Exception, optional): Exception information to be included in the log. Defaults to None.
            stack_level (int, optional): The stack level to be used for the log. Defaults to 1.
            monitor (str, optional): The monitor to associate with the log. Defaults to None.

        Returns:
            None
        """
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
        monitor: _Optional[str] = None,
    ) -> None:
        """
        Log a warning message.

        Args:
            message (str): The warning message to be logged.
            exc_info (Exception, optional): The exception information. Defaults to None.
            stack_level (int, optional): The stack level to be used for logging. Defaults to 1.
            monitor (str, optional): The monitor to be associated with the warning. Defaults to None.

        Returns:
            None
        """
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
        monitor: _Optional[str] = None,
    ) -> None:
        """
        Log an error message.

        Args:
            message (str): The error message to be logged.
            exc_info (Exception, optional): The exception information. Defaults to None.
            stack_level (int, optional): The stack level to be used for logging. Defaults to 1.
            monitor (str, optional): The monitor to be associated with the error. Defaults to None.
        """
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
        monitor: _Optional[str] = None,
    ) -> None:
        """
        Log a critical message.

        Args:
            message (str): The message to be logged.
            exc_info (Exception, optional): Exception information. Defaults to None.
            stack_level (int, optional): Stack level. Defaults to 1.
            monitor (str, optional): Monitor information. Defaults to None.

        Returns:
            None
        """
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
        directory_path: _Path,
        file_name: str,
        when: str,
        interval: int,
        backup_count: int,
        logging_formatter: str,
        date_formatter: str,
        stream_output: bool = False,
        telemetry_handler: _Optional[_logging.Handler] = None,
    ) -> _logging.Logger:
        """
        Create and configure a logger with the specified parameters.

        Args:
            name (str): The name of the logger.
            level (int): The logging level for the logger.
            directory_path (Path): The directory path where log files will be stored.
            file_name (str): The name of the log file.
            when (str): The interval at which log files should be rotated (e.g., 'midnight', 'D', 'H', 'M', 'S').
            interval (int): The number of intervals between log file rotations.
            backup_count (int): The number of backup log files to keep.
            logging_formatter (str): The logging formatter string.
            date_formatter (str): The date formatter string.
            stream_output (bool, optional): Whether to log messages to stdout as well. Defaults to False.
            telemetry_handler (Optional[logging.Handler]): The telemetry handler to be added to the logger. Defaults to None.

        Returns:
            logging.Logger: The configured logger.

        """
        logger = _logging.getLogger(name=name)
        logger.propagate = False

        if logger.hasHandlers():
            return logger

        formatter = _logging.Formatter(
            logging_formatter,
            datefmt=date_formatter,
        )

        monitoring_formatter = _logging.Formatter(
            f"[%(monitor)s] ({logging_formatter})",
            datefmt=date_formatter,
        )

        logger.setLevel(level)

        if stream_output:
            # Add a stream handler to log messages to stdout
            stream_handler = _logging.StreamHandler(stream=_sys.stdout)
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
            filter=_LevelFilter,
            filter_kwargs={
                "levels": [_logging.WARNING],
            },
        )

        # Add an error file handler to log error messages to a file
        error_time_rotating_handler = self._create_time_rotating_handler(
            file_path=directory_path / "errors.log",
            level=level,
            formatter=formatter,
            when=when,
            interval=interval,
            backup_count=backup_count,
            filter=_LevelFilter,
            filter_kwargs={
                "levels": [_logging.ERROR, _logging.CRITICAL],
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
            filter=_AttributeFilter,
            filter_kwargs={
                "param": "monitor",
            },
        )

        logger.addHandler(time_rotating_handler)
        logger.addHandler(warning_time_rotating_handler)
        logger.addHandler(error_time_rotating_handler)
        logger.addHandler(monitoring_time_rotating_handler)

        if telemetry_handler is not None:
            logger.addHandler(telemetry_handler)

        return logger

    def _create_time_rotating_handler(
        self,
        file_path: _Path,
        level: int,
        formatter: _logging.Formatter,
        when: str,
        interval: int,
        backup_count: int,
        filter: _Optional[_Callable[..., _logging.Filter]] = None,
        filter_kwargs: _Optional[_Dict[str, _Any]] = None,
    ) -> _TimedRotatingFileHandler:
        """
        Create a time rotating file handler for logging.

        Args:
            file_path (Path): The path to the log file.
            level (int): The logging level.
            formatter (logging.Formatter): The log message formatter.
            when (str): The type of interval at which the log file should rotate (e.g., 'midnight', 'H', 'D', 'W0' etc.).
            interval (int): The interval at which the log file should rotate.
            backup_count (int): The number of backup log files to keep.
            filter (Optional[Callable[..., logging.Filter]]): An optional filter function to apply to log records.
            filter_kwargs (Optional[Dict[str, Any]]): Optional keyword arguments to pass to the filter function.

        Returns:
            TimedRotatingFileHandler: The created time rotating file handler.
        """
        handler = _TimedRotatingFileHandler(
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
