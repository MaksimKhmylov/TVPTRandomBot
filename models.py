from peewee import Model, SqliteDatabase, CharField, IntegerField
from config import *

db = SqliteDatabase("TVPTRandomBot.db")

class User(Model):
    user_id = CharField(unique=True)
    username = CharField(unique=True)
    chat_id = CharField(unique=True)
    status = IntegerField(default=UserStatus.new.value)

    class Meta:
        database = db

