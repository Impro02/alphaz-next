# MODULES
import sys as _sys
from typing import Dict, Optional as _Optional
from loguru import logger as _logger
from opentelemetry import trace as _trace

_LOGGERS: Dict[str, "Logger"] = {}


class Logger:

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        enqueue: bool = False,
        stream_output: bool = False,
        colorize=True,
        format: _Optional[str] = None,
    ):
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
                format=format,
                level=level,
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
    def sub_logger(self):
        return self._logger

    def _log(self, level: str, message: str):
        span = _trace.get_current_span()
        otelSpanID = _trace.format_span_id(span.get_span_context().span_id)
        otelTraceID = _trace.format_trace_id(span.get_span_context().trace_id)

        with self._logger.contextualize(
            otelTraceID=otelTraceID,
            otelSpanID=otelSpanID,
        ):
            getattr(self._logger.opt(depth=2), level)(message)

    def info(self, message: str):
        self._log("info", message)

    def error(self, message: str):
        self._log("error", message)

    def warning(self, message: str):
        self._log("warning", message)

    def debug(self, message: str):
        self._log("debug", message)

    def trace(self, message: str):
        self._log("trace", message)

    def success(self, message: str):
        self._log("success", message)

    def critical(self, message: str):
        self._log("critical", message)

    def exception(self, message: str):
        self._log("exception", message)

    def catch(self, message: str):
        self._log("catch", message)
