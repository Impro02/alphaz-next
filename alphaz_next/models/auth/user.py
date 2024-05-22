# MODULES
from typing import List

# PYDANTIC
from pydantic import BaseModel, computed_field


class UserBaseSchema(BaseModel):
    """
    Represents a base schema for a user.
    """

    @computed_field  # type: ignore
    @property
    def permissions(self) -> List[str]:
        raise NotImplementedError(
            "This method must be implemented in the derived class."
        )
