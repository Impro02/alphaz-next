# MODULES
from typing import Any as _Any, Dict as _Dict

# PYDANTIC
from pydantic import (
    BaseModel as _BaseModel,
    ConfigDict as _ConfigDict,
    model_validator as _model_validator,
)

# MODELS
from alphaz_next.models.config._base.utils import (
    ReservedConfigItem as _ReservedConfigItem,
    replace_reserved_config as _replace_reserved_config,
)
from alphaz_next.models.config.api_config import (
    AlphaApiConfigSchema as _AlphaApiConfigSchema,
)


class AlphaConfigSchema(_BaseModel):
    """
    Schema for the AlphaConfig configuration.

    Attributes:
        model_config (ConfigDict): Configuration for the model.
        environment (str): Environment name.
        project_name (str): Project name.
        version (str): Version number.
        root (str): Root directory.
        port (int): Port number.
        workers (int): Number of workers.
        api_config (AlphaApiConfigSchema): Configuration for the Alpha API.
    """

    model_config = _ConfigDict(from_attributes=True)

    environment: str
    project_name: str
    version: str
    root: str
    port: int
    workers: int

    api_config: _AlphaApiConfigSchema

    @_model_validator(mode="before")
    @classmethod
    def validate_model(cls, data: _Dict[str, _Any]) -> _Dict:
        tmp = _replace_reserved_config(
            data,
            reserved_config=_ReservedConfigItem(
                environment=data.get("environment"),
                root=data.get("root"),
                project_name=data.get("project_name"),
            ),
        )

        reserved_fields = _ReservedConfigItem(
            environment=data.get("environment"),
            root=tmp.get("root"),
            project_name=tmp.get("project_name"),
        )

        for key, value in tmp.items():
            if isinstance(value, dict):
                tmp[key]["__reserved_fields__"] = reserved_fields

        return tmp
