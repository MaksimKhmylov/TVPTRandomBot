from pyrogram import Client, filters
import config
from config import UserStatus, ContestStatus
from models import User, Contest, db

API_ID = config.API_ID
API_HASH = config.API_HASH
BOT_TOKEN =  config.API_TOKEN


app = Client("TVPTbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("create"))
def create_contest(client, message):
    contest, created = Contest.get_or_create()
    if created:
        client.send_message("Введите текст")
        contest.status = ContestStatus.winners



@app.on_message(filters.command("start"))
def start(client, message):
    message_data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "chat_id": message.chat.id,
    }

    user, created = User.get_or_create(**message_data)

    message.reply_text(f"Привет! Твой юзер: @{message.from_user.username}")

#ВАЖНО!!! ЭТА ФУНКЦИЯ В КОНЦЕ ПРОГРАММЫ!!!
@app.on_message(filters.text) #Это основна создания конкурса
def create_more_contest(client, message):
    user = User.get(User.user_id == message.from_user.id)
    # contest, created = Contest.get()
    # if created:
    #     if contest.status == ContestStatus.winners:
    #         client.send_message()
    #         contest.text = message.text
    #         contest.status = ContestStatus.channel
    #     elif contest.status == ContestStatus.channel:
    #         client.send_message()
    #         contest.winners = message.text
    #         contest.status = ContestStatus.date_start
    #     elif contest.status == ContestStatus.date_start:
    #         client.send_message()
    #         contest.date_start = message.text
    #         contest.status = ContestStatus.date_end
    #     elif contest.status == ContestStatus.date_end:
    #         client.send_message()
    #         contest.date_end = message.text
    #         contest.status = ContestStatus.finished
    pass

if __name__ == "__main__":
    app.run()