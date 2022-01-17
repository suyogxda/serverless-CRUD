from typing import Optional, Literal
import pydantic


class CreateReview(pydantic.BaseModel):
    item_id: str
    stars: Literal[1, 2, 3, 4, 5]
    type: Literal["dish", "restaurant"]
    description: Optional[str]
