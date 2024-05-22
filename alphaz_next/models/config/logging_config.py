# MODULES
import logging as _logging
from typing import Annotated as _Annotated, List as _List, Optional as _Optional

# OPENTELEMETRY
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# PYDANTIC
from pydantic_core.core_schema import FieldValidationInfo as _FieldValidationInfo
from pydantic import (
    BaseModel as _BaseModel,
    ConfigDict as _ConfigDict,
    Field as _Field,
    StringConstraints as _StringConstraints,
    computed_field as _computed_field,
    field_validator as _field_validator,
)

LOGGING_LEVEL = {
    "CRITICAL": _logging.CRITICAL,
    "ERROR": _logging.ERROR,
    "WARNING": _logging.WARNING,
    "INFO": _logging.INFO,
    "DEBUG": _logging.DEBUG,
}


class LoggingSchema(_BaseModel):
    """
    Represents the configuration schema for logging.

    Attributes:
        model_config (ConfigDict): Configuration dictionary for the model.
        format (Optional[str]): Logging format.
        level (str): Logging level.
        rotation (Optional[str]): Log rotation.
        retention (Optional[int]): Log retention.
        excluded_routers (List[str]): List of excluded routers.
        level_code (int): Logging level code.
    """

    model_config = _ConfigDict(from_attributes=True)

    level: _Annotated[
        str,
        _StringConstraints(
            strip_whitespace=True,
            to_upper=True,
        ),
    ]
    format: str
    uvicorn_format: str
    date_format: str
    rotation: _Optional[str] = _Field(default=None)
    retention: _Optional[int] = _Field(default=None)
    excluded_routers: _List[str] = _Field(default_factory=lambda: [])

    @_field_validator("format")
    @classmethod
    def validate_format(cls, value: str, info: _FieldValidationInfo) -> str:
        if value is not None:
            LoggingInstrumentor().instrument(logging_format=value)

        return value

    @_field_validator("level")
    @classmethod
    def validate_level(cls, value: str, info: _FieldValidationInfo) -> str:
        if value not in LOGGING_LEVEL:
            raise ValueError(f"{info.field_name} is not valid")

        return value

    @_computed_field  # type: ignore
    @property
    def level_code(self) -> int:
        return LOGGING_LEVEL.get(self.level.upper(), 0)
