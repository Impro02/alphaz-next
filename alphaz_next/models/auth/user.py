# MODULES
from typing import List

# PYDANTIC
from pydantic import BaseModel, computed_field


class UserBaseSchema(BaseModel):
    """
    Represents a base schema for a user.
    """

    @property
    @computed_field
    def permissions(self) -> List[str]:
        raise NotImplementedError(
            "This method must be implemented in the derived class."
        )
