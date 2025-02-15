import random

from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import ContestStatus, UserStatus
from models import User, UserChannels, Contest


cancel_button = [InlineKeyboardButton("Отмена", callback_data="cancel_action")]
cancel_key = InlineKeyboardMarkup([cancel_button])


def add_new_channel(message, client, user):
    """Добавление канала в аккаунт юзера"""
    # Создание списка админов и владельца канала
    members = client.get_chat_members(message.forward_from_chat.id)
    admins = []
    for member in members:
        if member.status == ChatMemberStatus.ADMINISTRATOR or member.status == ChatMemberStatus.OWNER:
            admins.append(member.user.id)

    if int(user.user_id) in admins:
        channel_id = message.forward_from_chat.id
        channel_name = message.forward_from_chat.title
        UserChannels.create(user_id=user.user_id, channel_id=channel_id, channel_name=channel_name)
        client.send_message(message.chat.id, f"Канал {channel_name} сохранен")
        user.status = UserStatus.STANDBY
        user.save()
    else:
        client.send_message(message.chat.id, "Ошибка 403: Вы не являетесь админом канала!")
        user.status = UserStatus.STANDBY
        user.save()


def contest_text(message, client, contest):
    """Добавление текста конкурса"""
    if contest.hello_sent:
        contest.hello_sent = False
        contest.text = message.text
        contest.status = ContestStatus.WINNERS
        contest.save()
        client.send_message(message.chat.id, "Текст для конкурса сохранен")
        contest_winner(message, client, contest)
    else:
        client.send_message(message.chat.id, "Введите текст конкурса", reply_markup=cancel_key)
        contest.hello_sent = True
        contest.save()

def contest_winner(message, client, contest):
    """Добавление количества победителей в конкурс"""
    if contest.hello_sent:
        contest.hello_sent = False
        if message.text.isdigit():
            contest.winners = int(message.text)
            contest.status = ContestStatus.CHANNEL
            contest.save()
            client.send_message(message.chat.id, "Кол-во победителей сохранено")
            contest_channel(message, client)
        else:
            client.send_message(message.chat.id, "Напишите кол-во победителей **ЧИСЛОМ**", reply_markup=cancel_key)
    else:
        client.send_message(message.chat.id, "Напишите кол-во победителей **числом**", reply_markup=cancel_key)
        contest.hello_sent = True
        contest.save()


def contest_channel(message, client):
    """Добавление канала вывода результатов конкурса"""
    user = User.get(User.user_id == message.from_user.id)
    channels = UserChannels.select().where(UserChannels.user == user.user_id)
    channels = [(channel.channel_name, channel.channel_id) for channel in channels]
    buttons = []
    for channel in channels:
        buttons.append([InlineKeyboardButton(channel[0], callback_data=f"CHID_{channel[1]}")])
    buttons.append(cancel_button)
    channel_keys = InlineKeyboardMarkup(buttons)
    client.send_message(message.chat.id, "Выберите канал", reply_markup=channel_keys)


def contest_info(contest_id, client):
    """Отправить в канал проведения конкурса информационное сообщение"""
    contest = Contest.get(Contest.id == contest_id)
    client.send_message(contest.channel, contest.text)


def contest_run(contest_id, client, callback_query):
    """Выполнить конкурс"""
    contest = Contest.get(Contest.id == contest_id)
    members = client.get_chat_members(contest.channel)
    players = []
    for member in members:
        if member.status == ChatMemberStatus.MEMBER:
            players.append(member)
    if len(players) < contest.winners:
        callback_query.edit_message_text(
            f"Количество подписчиков ({len(players)}) канала меньше количества победителей ({contest.winners})",
            reply_markup=cancel_key)
    else:
        winners = []
        for _ in range(contest.winners):
            player = random.choice(players)
            winners.append("@"+(player.user.username))
            players.remove(player)
        contest.status = ContestStatus.DONE
        contest.save()
        callback_query.edit_message_text(f"Конкурс проведен, победители: {', '.join(winners)}")
        client.send_message(contest.channel, f"ПОБЕДИТЕЛИ КОНКУРСА: {', '.join(winners)}")
