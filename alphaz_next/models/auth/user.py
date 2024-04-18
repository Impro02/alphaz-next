# MODULES
from typing import List

# PYDANTIC
from pydantic import BaseModel, computed_field


class UserBaseSchema(BaseModel):
    """
    Represents a base schema for a user.
    """

    @computed_field
    @property
    def permissions(self) -> List[str]:
        NotImplementedError("This method must be implemented in the derived class.")
