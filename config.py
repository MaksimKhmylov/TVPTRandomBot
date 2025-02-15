import enum

API_ID = 22543588
API_HASH = '7e20f617e664855078a41a98df729c1c'
API_TOKEN = '7051266336:AAFsZr-ZuitAV2nvRSrJMCiYX7MtwS1KSGw'

class UserStatus(enum.Enum):
    standby = 1
    edit_contest = 2
    add_channel = 3

class ContestStatus(enum.Enum):
    text = 1
    winners = 2
    channel = 3
    finished = 4
    done = 5
