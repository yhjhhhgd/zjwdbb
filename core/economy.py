from database import get_session
from models import User
import random


def reward(user):
    user.xp += random.randint(8, 18)
    coins_before = user.coins
    user.coins += random.randint(2, 10)
    user.qi += random.randint(8, 15)

    # TODO: 师徒分成（暂时关闭，避免报错）
    # coins_gained = user.coins - coins_before
    # if coins_gained > 0:
    #     try:
    #         from handlers.invite import give_master_share
    #         ...
    #     except:
    #         pass   # 防止崩溃

def level_up(user):
    while user.xp >= user.level * 500:
        user.xp -= user.level * 500
        user.level += 1
        user.luck += 0.05
        user.coins += 250


def inflation_control(user):
    if user.coins > 50000:
        user.coins = int(user.coins * 0.98)
