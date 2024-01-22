# PYDANTIC
from typing import Annotated, List

# PYDANTIC
from pydantic_core.core_schema import FieldValidationInfo
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
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
    excluded_routers: List[str] = Field(default_factory=lambda: [])

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
