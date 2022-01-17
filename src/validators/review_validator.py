from typing import Optional, Literal
from pydantic import BaseModel, root_validator

from src.errors.generic_error import GenericError


class CreateReview(BaseModel):
    item_id: str
    stars: Literal[1, 2, 3, 4, 5]
    type: Literal["dish", "restaurant"]
    description: Optional[str]


class UpdateReview(BaseModel):
    stars: Optional[Literal[1, 2, 3, 4, 5]]
    description: Optional[str]

    @root_validator(pre=True)
    def at_least_one(cls, v):
        if not len(v):
            raise GenericError(
                "At least one field is required to update the review", 400
            )
        return v

    class Config:
        extra = "ignore"
