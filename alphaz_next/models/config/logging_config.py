# PYDANTIC
from typing import Annotated

# PYDANTIC
from pydantic import (
    BaseModel,
    ConfigDict,
    FieldValidationInfo,
    PositiveInt,
    StringConstraints,
    computed_field,
    field_validator,
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


class TimeRotatingSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    when: str
    interval: PositiveInt
    backup_count: PositiveInt


class LoggingSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    level: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            to_upper=True,
        ),
    ]
    time_rotating: TimeRotatingSchema

    @field_validator("level")
    @classmethod
    def validate_level(cls, value: str, info: FieldValidationInfo):
        if value not in LOGGING_LEVEL:
            raise ValueError(f"{info.field_name} is not valid")

        return value

    @computed_field
    @property
    def level_code(self) -> int:
        return LOGGING_LEVEL.get(self.level)
