import enum

API_ID = 22543588
API_HASH = '7e20f617e664855078a41a98df729c1c'
API_TOKEN = '7051266336:AAFsZr-ZuitAV2nvRSrJMCiYX7MtwS1KSGw'

class UserStatus(enum.Enum):
    standby = 1
    edit = 2

class ContestStatus(enum.Enum):
    text = 1
    winners = 2
    channel = 3
    date_start = 4
    date_end = 5
    finished = 6
