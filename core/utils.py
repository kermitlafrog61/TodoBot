from peewee import PostgresqlDatabase, Model

from core.settings import settings

db_connection = PostgresqlDatabase(settings.db_url)

def db(func):
    def wrapper(*args, **kwargs):
        db_connection.connect()
        try:
            return func(*args, **kwargs)
        finally:
            db_connection.close()
    return wrapper


class BaseModel(Model):
    class Meta:
        database = db_connection
