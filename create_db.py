from peewee import SqliteDatabase
from models import User, Contest, UserChannels

db = SqliteDatabase("TVPTRandomBot.db")
db.connect()
db.create_tables([User, Contest, UserChannels])
