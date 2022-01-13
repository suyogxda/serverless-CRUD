from typing import Optional
import pydantic


class CreateNews(pydantic.BaseModel):
    title: str
    description: Optional[str]
