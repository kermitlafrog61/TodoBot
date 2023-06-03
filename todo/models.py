from datetime import datetime

import peewee as pw

from core.utils import BaseModel


class Todo(BaseModel):
    title = pw.CharField(max_length=255)
    description = pw.TextField(null=True)
    completed = pw.BooleanField(default=False, null=True)
    created_at = pw.DateTimeField(default=datetime.now)
    due_to = pw.DateTimeField(default=None, null=True)
