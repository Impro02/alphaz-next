# MODULES
import sys as _sys
from typing import Dict as _Dict, Optional as _Optional, cast as _cast
from loguru import logger as _logger, Logger as _Logger, _defaults

# OPENTELEMETRY
from opentelemetry import trace as _trace

_LOGGERS: _Dict[str, "Logger"] = {}


class Logger:

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        enqueue: bool = False,
        stream_output: bool = False,
        colorize: bool = True,
        format: _Optional[str] = None,
    ) -> None:
        self._is_new = True
        if name in _LOGGERS:
            saved_logger = _LOGGERS[name]
            self._logger = saved_logger.sub_logger
            self._name = saved_logger.name
            self._level = saved_logger.level
            self._is_new = False
            return

        self._name = name
        self._level = level

        self._logger = _logger.bind(service=name)

        if stream_output:
            self._logger.add(
                _sys.stderr,
                level=level,
                format=format or _cast(str, _defaults.LOGURU_FORMAT),
                colorize=colorize,
                filter=lambda record: record["extra"].get("service") == name,
                enqueue=enqueue,
            )

        _LOGGERS[name] = self

    @property
    def name(self) -> str:
        return self._name

    @property
    def level(self) -> str:
        return self._level

    @property
    def is_new(self) -> bool:
        return self._is_new

    @property
    def sub_logger(self) -> _Logger:
        return self._logger

    def _log(self, level: str, message: str) -> None:
        span = _trace.get_current_span()
        otelSpanID = _trace.format_span_id(span.get_span_context().span_id)
        otelTraceID = _trace.format_trace_id(span.get_span_context().trace_id)

        with self._logger.contextualize(
            otelTraceID=otelTraceID,
            otelSpanID=otelSpanID,
        ):
            getattr(self._logger.opt(depth=2), level)(message)

    def info(self, message: str) -> None:
        self._log("info", message)

    def error(self, message: str) -> None:
        self._log("error", message)

    def warning(self, message: str) -> None:
        self._log("warning", message)

    def debug(self, message: str) -> None:
        self._log("debug", message)

    def trace(self, message: str) -> None:
        self._log("trace", message)

    def success(self, message: str) -> None:
        self._log("success", message)

    def critical(self, message: str) -> None:
        self._log("critical", message)

    def exception(self, message: str) -> None:
        self._log("exception", message)

    def catch(self, message: str) -> None:
        self._log("catch", message)
