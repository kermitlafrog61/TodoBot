import logging
from typing import List

from peewee import DoesNotExist, IntegrityError

from core.utils import db

from .models import Todo
from .schemas import TodoDetailSchema, TodoListSchema


logger = logging.getLogger(__name__)


@db
def create_todo(title):
    try:
        todo = Todo.create(title=title)
    except IntegrityError as e:
        todo = 0
        logger.error(e)

    return todo


@db
def list_todos() -> List[Todo]:
    todos = Todo.select()
    return [TodoListSchema.from_orm(todo) for todo in todos]


@db
def retrieve_todo(id: int) -> Todo:
    todo = Todo.get_by_id(id)

    if not todo:
        return 0

    return TodoDetailSchema.from_orm(todo)


@db
def update_todo(id, key, value):
    try:
        key_value = {key: value}
        post = Todo.get_by_id(id)
        updated = (post.update(
            **key_value)
            .execute())

    except DoesNotExist:
        updated = 0

    return f"Updated {updated}"


@db
def destroy_todo(id):
    try:
        todo = Todo.get_by_id(id)
        todo.delete_instance()

    except DoesNotExist:
        todo = 0

    return todo
