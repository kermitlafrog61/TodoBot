from datetime import datetime
from typing import Any, List, Optional

from peewee import ManyToManyQuery
from pydantic import BaseModel


class TodoListSchema(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True


class TodoDetailSchema(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: Optional[str]
    created_at: datetime
    due_to: Optional[str]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# class PostCreateSchema(BaseModel):
#     title: str
#     description: Optional[str]
#     year: date
#     country: str
#     genres: List[str]

#     class Config:
#         orm_mode = True
