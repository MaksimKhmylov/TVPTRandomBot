from pyrogram import Client, filters
import config
from config import UserStatus
from models import *

API_ID = config.API_ID
API_HASH = config.API_HASH
BOT_TOKEN =  config.API_TOKEN


app = Client("TVPTbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start(client, message):
    message_data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "chat_id": message.chat.id,
    }

    user, created = User.get_or_create(**message_data)

    message.reply_text(f"Привет! Твой юзер: @{message.from_user.username}")

if __name__ == "__main__":
    app.run()