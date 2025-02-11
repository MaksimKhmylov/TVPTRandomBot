from peewee import Model, SqliteDatabase, CharField, IntegerField, ForeignKeyField, TextField, DateField
from config import *

db = SqliteDatabase("TVPTRandomBot.db")

class User(Model):

    user_id = CharField(unique=True)
    username = CharField(unique=True)
    chat_id = CharField(unique=True)
    status = IntegerField(default=UserStatus.standby.value)

    class Meta:
        database = db

class Contest(Model):

    user = ForeignKeyField(User, backref='contests')
    text = TextField(null=True)
    winners = IntegerField(null=True)
    channel = CharField(null=True)
    date_start = DateField(null=True)
    date_end = DateField(null=True)
    status = IntegerField(default=ContestStatus.text.value,)

    class Meta:
        database = db