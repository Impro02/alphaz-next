# MODULES
from typing import List as _List

# PYDANTIC
from pydantic import BaseModel as _BaseModel, computed_field as _computed_field


class UserBaseSchema(_BaseModel):
    """
    Represents a base schema for a user.
    """

    @_computed_field  # type: ignore
    @property
    def permissions(self) -> _List[str]:
        raise NotImplementedError(
            "This method must be implemented in the derived class."
        )
