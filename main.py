from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import UserStatus, ContestStatus, API_ID, API_HASH, API_TOKEN
from models import User, Contest, UserChannels
from utils import contest_text, contest_winner, contest_channel, contest_run, contest_info, cancel_key, add_new_channel, \
    cancel_button

app = Client("TVPTbot", api_id=API_ID, api_hash=API_HASH, bot_token=API_TOKEN)


def handle_user_message(user, message, client, contest: Contest = None):
    """Функция обработки введенных данных от пользователя"""
    if user.status == UserStatus.ADD_CHANNEL:
        if message.text == "/add_channel":
            client.send_message(
                message.chat.id,
                "Перешлите сообщение(без картинки) из канала для его добавления",
                reply_markup=cancel_key)
        try:
            add_new_channel(message, client, user)
        except Exception as e:
            if message.text != "/add_channel":
                client.send_message(
                    message.chat.id,
                    f"Канал не добавлен: возможно вы пытаетесь добавить существующий канал. Ошибка: {e}",
                    reply_markup=cancel_key)
                user.status = UserStatus.STANDBY
                user.save()

    elif user.status == UserStatus.EDIT_CONTEST:
        match contest.status:
            case ContestStatus.TEXT:
                contest_text(message, client, contest)
            case ContestStatus.WINNERS:
                contest_winner(message, client, contest)
            case ContestStatus.CHANNEL:
                contest_channel(message, client)
    else:
        client.send_message(message.chat.id, "Неопознанное сообщение")


def get_contest(message):
    """Создать или вернуть незаконченный конкурс"""
    user = User.get(User.user_id == message.from_user.id)
    query = (Contest.select().where(
        (Contest.status != ContestStatus.FINISHED) &
        (Contest.status != ContestStatus.DONE) &
        (Contest.user == user.user_id)
    ))

    if len(query) == 0:
        return Contest.create(user_id=message.from_user.id), user
    else:
        return query[0], user


@app.on_message(filters.command("start"))
def start(client, message):
    """Команда Start"""
    message_data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "chat_id": message.chat.id,
    }
    user, created = User.get_or_create(**message_data)
    if created:
        message.reply_text(
            f"Привет, @{message.from_user.username}, твой аккаунт создан")
    else:
        message.reply_text(
            f"Привет, @{message.from_user.username}, с возвращением!")


@app.on_message(filters.command("add_contest"))
def create_contest(client, message):
    """Команда Add_contest"""
    contest, user = get_contest(message)
    user.status = UserStatus.EDIT_CONTEST
    user.save()
    handle_user_message(user, message, client, contest)


@app.on_message(filters.command("add_channel"))
def add_channel(client, message):
    """Команда Add_channel"""
    user = User.get(User.user_id == message.from_user.id)
    user.status = UserStatus.ADD_CHANNEL
    user.save()
    handle_user_message(user, message, client)


@app.on_message(filters.command("my_channels"))
def my_channels(client, message):
    """Команда My_channels"""
    user = User.get(User.user_id == message.from_user.id)
    channels = UserChannels.select().where(UserChannels.user == user.user_id)
    channels = [channel.channel_name for channel in channels]
    client.send_message(chat_id=message.chat.id, text=f"Ваши каналы: {', '.join(channels)}")


@app.on_message(filters.command("my_contests"))
def my_contests(client, message):
    """Команда My_contests"""
    user = User.get(User.user_id == message.from_user.id)
    contests = Contest.select().where(
        (Contest.user == user.user_id) &
        (Contest.status == ContestStatus.FINISHED)
    )
    contests = [(contest.text, contest.id) for contest in contests]
    buttons = []
    for contest in contests:
        buttons.append([InlineKeyboardButton(contest[0], callback_data=f"CTID_{contest[1]}")])
    buttons.append(cancel_button)
    contest_keys = InlineKeyboardMarkup(buttons)

    client.send_message(message.chat.id, "Ваши конкурсы", reply_markup=contest_keys)


@app.on_message(filters.text)
def handle_text(client, message):
    """Обработка любых текстовых сообщений"""
    contest, user = get_contest(message)
    handle_user_message(user, message, client, contest)


@app.on_callback_query()
def callback_query(client, callback_query):
    """Обработка нажатий кнопок чата"""

    if callback_query.data == "cancel_action":
        # Обработка кнопки Отмена
        contest, user = get_contest(callback_query)
        contest.delete_instance()
        user.status = UserStatus.STANDBY
        user.save()
        callback_query.answer("Вы отменили действие")
        callback_query.edit_message_text("Вы отменили действие")

    if callback_query.data.startswith("CHID"):
        # Обработка кнопки выбора канала для проведения конкурса
        channel_id = callback_query.data.split("CHID_")[1]
        contest, user = get_contest(callback_query)
        contest.channel = channel_id
        contest.status = ContestStatus.FINISHED
        user.status = UserStatus.STANDBY
        user.save()
        contest.save()
        callback_query.answer("Конкурс сохранен")
        callback_query.edit_message_text("Вы создали конкурс!")

    if callback_query.data.startswith("CTID"):
        # Обработка кнопки выбора конкурса пользователя, для формирования кнопок Оповещения и Проведения конкурса
        contest_id = callback_query.data.split("CTID_")[1]
        contest_keys = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Оповестить", callback_data=f"CTINFO_{contest_id}")],
                [InlineKeyboardButton("Провести", callback_data=f"CTRUN_{contest_id}")]
            ]
        )
        callback_query.edit_message_text("Выполнить действие", reply_markup=contest_keys)

    if callback_query.data.startswith("CTINFO"):
        # Обработка кнопки посылающее сообщение в чат конкурса
        contest_id = callback_query.data.split("CTINFO_")[1]
        contest_info(contest_id, client)
        callback_query.edit_message_text("Сообщение отправлено")

    if callback_query.data.startswith("CTRUN"):
        # Обработка кнопки выполнения конкурса
        contest_id = callback_query.data.split("CTRUN_")[1]
        contest_run(contest_id, client, callback_query)


if __name__ == "__main__":
    app.run()
