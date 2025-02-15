from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from config import UserStatus, ContestStatus
from models import User, Contest, UserChannels
from utils import contest_text, contest_winner, contest_channel, contest_run, contest_info

cancel_channel_key = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("Отмена", callback_data="cancel_channel_add")]
    ]
)

API_ID = config.API_ID
API_HASH = config.API_HASH
BOT_TOKEN =  config.API_TOKEN

app = Client("TVPTbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def handle_user_message(user, message, client, contest: Contest = None):
    if user.status == UserStatus.add_channel.value:
        if message.text == "/add_channel":
            client.send_message(message.chat.id, "Перешлите сообщение(без картинки) из канала для его добавления", reply_markup=cancel_channel_key)
        try:
            channel_id = message.forward_from_chat.id
            channel_name = message.forward_from_chat.title
            channel = UserChannels.create(user_id=user.user_id, channel_id=channel_id, channel_name=channel_name)
            channel.save()
            client.send_message(message.chat.id, f"Канал {channel_name} сохранен")
            user.status = UserStatus.standby.value
            user.save()
        except Exception as e:
            if message.text != "/add_channel":
                client.send_message(message.chat.id, f"Канал не добавлен: возможно вы пытаетесь добавить существующий канал. Ошибка: {e}")

    elif user.status == UserStatus.edit_contest.value:
        match contest.status:
            case ContestStatus.text.value:
                contest_text(message, client, contest)
            case ContestStatus.winners.value:
                contest_winner(message, client, contest)
            case ContestStatus.channel.value:
                contest_channel(message, client, contest)
    else:
        client.send_message(message.chat.id, "Неопознанное сообщение")

def get_contest(message):
    user = User.get(User.user_id == message.from_user.id)
    query = (Contest.select().where(
        (Contest.status != ContestStatus.finished.value) &
        (Contest.status != ContestStatus.done.value) &
        (Contest.user == user.user_id)
    ))

    if len(query) == 0:
        return Contest.create(user_id=message.from_user.id), user
    else:
        return query[0], user

@app.on_message(filters.command("start"))
def start(client, message):
    message_data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "chat_id": message.chat.id,
    }

    user, created = User.get_or_create(**message_data)

    message.reply_text(f"Привет! Твой юзер: @{message.from_user.username}")


@app.on_message(filters.command("add_contest"))
def create_contest(client, message):
    contest, user = get_contest(message)
    user.status = UserStatus.edit_contest.value
    user.save()
    handle_user_message(user, message, client, contest)

@app.on_message(filters.command("add_channel"))
def edit_channels(client, message):
    user = User.get(User.user_id == message.from_user.id)
    user.status = UserStatus.add_channel.value
    user.save()
    handle_user_message(user, message, client)

@app.on_message(filters.command("my_channels"))
def my_channels(client, message):
    user = User.get(User.user_id == message.from_user.id)
    channels = UserChannels.select().where(UserChannels.user == user.user_id)
    channels = [channel.channel_name for channel in channels]
    client.send_message(chat_id=message.chat.id, text=f"Ваши каналы: {', '.join(channels)}")

@app.on_message(filters.command("my_contests"))
def my_contests(client, message):
    user = User.get(User.user_id == message.from_user.id)
    contests = Contest.select().where(Contest.user == user.user_id)
    contests = [(contest.text, contest.id) for contest in contests]
    buttons = []
    for contest in contests:
        buttons.append([InlineKeyboardButton(contest[0], callback_data=f"CTID_{contest[1]}")])
    contest_keys = InlineKeyboardMarkup(buttons)

    client.send_message(message.chat.id, "Ваши конкурсы", reply_markup=contest_keys)

@app.on_message(filters.text)
def handle_text(client, message):
    contest, user = get_contest(message)
    handle_user_message(user, message, client, contest)

@app.on_callback_query()
def callback_query(client, callback_query):
    if callback_query.data == "cancel_channel_add":
        callback_query.answer("Отмена добавления канала")
        callback_query.edit_message_text("Вы отменили добавление канала")
        user = User.get(User.user_id == callback_query.from_user.id)
    if callback_query.data.startswith("CHID"):
        channel_id = callback_query.data.split("CHID_")[1]
        contest, user = get_contest(callback_query)
        contest.channel = channel_id
        contest.status = ContestStatus.finished.value
        user.status = UserStatus.standby.value
        user.save()
        contest.save()
        callback_query.answer("Конкурс сохранен")
        callback_query.edit_message_text("Вы создали конкурс!")
    if callback_query.data.startswith("CTID"):
        contest_id = callback_query.data.split("CTID_")[1]
        contest = Contest.get(Contest.id == contest_id)
        contest_keys = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Оповестить", callback_data=f"CTINFO_{contest_id}")],
                [InlineKeyboardButton("Провести", callback_data=f"CTRUN_{contest_id}")]
            ]
        )
        callback_query.edit_message_text("Выполнить действие", reply_markup=contest_keys)
    if callback_query.data.startswith("CTINFO"):
        contest_id = callback_query.data.split("CTINFO_")[1]
        contest_info(contest_id, client)




if __name__ == "__main__":
    app.run()