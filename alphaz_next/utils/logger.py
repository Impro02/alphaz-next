# MODULES
import sys
import logging
import unidecode
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional


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
    ):
        if file_name is None:
            file_name = name

        error_name = "errors"
        warning_name = "warnings"
        monitoring_name = "monitoring"

        directory_path = Path(directory)
        directory_path.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

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
        exc_info=None,
        monitor: Optional[str] = None,
    ):
        self._logger.info(message, exc_info=exc_info)
        if monitor is not None:
            self._monitoring_logger.info(
                self._process_monitoring_message(message=message, monitor=monitor),
                exc_info=exc_info,
            )

    def warning(
        self,
        message,
        exc_info=None,
        monitor: Optional[str] = None,
    ):
        self._logger.warning(message, exc_info=exc_info)
        self._warning_logger.warning(message, exc_info=exc_info)
        if monitor is not None:
            self._monitoring_logger.info(
                self._process_monitoring_message(message=message, monitor=monitor),
                exc_info=exc_info,
            )

    def error(
        self,
        message,
        exc_info=None,
        monitor: Optional[str] = None,
    ):
        self._logger.error(message, exc_info=exc_info)
        self._error_logger.error(message, exc_info=exc_info)
        if monitor is not None:
            self._monitoring_logger.info(
                self._process_monitoring_message(message=message, monitor=monitor),
                exc_info=exc_info,
            )

    def critical(
        self,
        message,
        exc_info=None,
        monitor: Optional[str] = None,
    ):
        self._logger.critical(message, exc_info=exc_info)
        self._error_logger.critical(message, exc_info=exc_info)
        if monitor is not None:
            self._monitoring_logger.info(
                self._process_monitoring_message(message=message, monitor=monitor),
                exc_info=exc_info,
            )

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
