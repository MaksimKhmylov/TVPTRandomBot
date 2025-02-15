from peewee import Model, SqliteDatabase, CharField, IntegerField, ForeignKeyField, TextField, DateField, BooleanField
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
    status = IntegerField(default=ContestStatus.text.value,)
    hello_sent = BooleanField(default=False)

    class Meta:
        database = db

class UserChannels(Model):
    user = ForeignKeyField(User, backref='channels')
    channel_id = IntegerField(unique=True)
    channel_name = CharField()

    class Meta:
        database = db
