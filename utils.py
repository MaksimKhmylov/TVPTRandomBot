import random

from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import enums

from config import ContestStatus
from models import User, UserChannels, Contest


def contest_text(message, client, contest):
    if contest.hello_sent:
        contest.hello_sent = False
        contest.text = message.text
        contest.status = ContestStatus.winners.value
        contest.save()
        client.send_message(message.chat.id, "Текст для конкурса сохранен")
        contest_winner(message, client, contest)
    else:
        client.send_message(message.chat.id, "Введите текст конкурса")
        contest.hello_sent = True
        contest.save()

def contest_winner(message, client, contest):
    if contest.hello_sent:
        contest.hello_sent = False
        if message.text.isdigit():
            contest.winners = int(message.text)
            contest.status = ContestStatus.channel.value
            contest.save()
            client.send_message(message.chat.id, "Кол-во победителей сохранено")
            contest_channel(message, client, contest)
        else:
            client.send_message(message.chat.id, "Напишите кол-во победителей **ЧИСЛОМ**")
    else:
        client.send_message(message.chat.id, "Напишите кол-во победителей **числом**")
        contest.hello_sent = True
        contest.save()


def contest_channel(message, client, contest):
    user = User.get(User.user_id == message.from_user.id)
    channels = UserChannels.select().where(UserChannels.user == user.user_id)
    channels = [(channel.channel_name, channel.channel_id) for channel in channels]
    buttons = []
    for channel in channels:
        buttons.append([InlineKeyboardButton(channel[0], callback_data=f"CHID_{channel[1]}")])
    channel_keys = InlineKeyboardMarkup(buttons)

    client.send_message(message.chat.id, "Выберите канал", reply_markup=channel_keys)
    contest.hello_sent = True
    contest.save()

def contest_info(contest_id, client):
    contest = Contest.get(Contest.id == contest_id)
    client.send_message(contest.channel, contest.text)

def contest_run(contest_id, client):
    contest = Contest.get(Contest.id == contest_id)
    members = client.get_chat_members(contest.channel)
    players = []
    for member in members:
        if member.status == ChatMemberStatus.MEMBER:
            players.append(member)
    winners = []
    for _ in range(contest.winners):
        player = random.choice(players)
        winners.append("@"+(player.user.username))
        players.remove(player)
    client.send_message(contest.channel, f"ПОБЕДИТЕЛИ КОНКУРСА: {', '.join(winners)}")


