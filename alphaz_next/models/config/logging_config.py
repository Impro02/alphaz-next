# PYDANTIC
from typing import Annotated as _Annotated, List as _List

# PYDANTIC
from pydantic_core.core_schema import FieldValidationInfo as _FieldValidationInfo
from pydantic import (
    BaseModel as _BaseModel,
    ConfigDict as _ConfigDict,
    Field as _Field,
    PositiveInt as _PositiveInt,
    StringConstraints as _StringConstraints,
    computed_field as _computed_field,
    field_validator as _field_validator,
)

LOGGING_LEVEL = {
    "CRITICAL": 50,
    "FATAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "WARN": 30,
    "INFO": 20,
    "DEBUG": 10,
    "NOTSET": 0,
}


class TimeRotatingSchema(_BaseModel):
    """
    Represents the configuration schema for time-based rotating log files.

    Attributes:
        when (str): The time interval at which the log files should rotate.
        interval (PositiveInt): The number of time units between each rotation.
        backup_count (PositiveInt): The maximum number of backup log files to keep.
    """

    model_config = _ConfigDict(from_attributes=True)

    when: str
    interval: _PositiveInt
    backup_count: _PositiveInt


class LoggingSchema(_BaseModel):
    """
    Represents the configuration schema for logging.

    Attributes:
        model_config (ConfigDict): Configuration dictionary for the model.
        level (str): Logging level.
        time_rotating (TimeRotatingSchema): Schema for time rotating configuration.
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
    time_rotating: TimeRotatingSchema
    excluded_routers: _List[str] = _Field(default_factory=lambda: [])

    @_field_validator("level")
    @classmethod
    def validate_level(cls, value: str, info: _FieldValidationInfo):
        if value not in LOGGING_LEVEL:
            raise ValueError(f"{info.field_name} is not valid")

        return value

    @_computed_field
    @property
    def level_code(self) -> int:
        return LOGGING_LEVEL.get(self.level)
