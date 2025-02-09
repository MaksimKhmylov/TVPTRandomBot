from peewee import SqliteDatabase
from models import User

db = SqliteDatabase("TVPTRandomBot.db")
db.connect()
db.create_tables([User])
