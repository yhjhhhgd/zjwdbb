from database import get_session
from models import User
import random


def reward(user):
    user.xp += random.randint(8, 15)
    coins_before = user.coins
    user.coins += random.randint(1, 5)
    user.qi += random.randint(8, 15)

    # 新增：师徒分成
    coins_gained = user.coins - coins_before
    if coins_gained > 0:
        from handlers.invite import give_master_share
        with get_session() as s:          # 需要 import get_session
            # 先把 user 存一下
            session_user = s.get(User, user.user_id)  # 确保是 session 里的对象
            if session_user:
                give_master_share(s, session_user, coins_gained)
                s.commit()


def level_up(user):
    while user.xp >= user.level * 500:
        user.xp -= user.level * 500
        user.level += 1
        user.luck += 0.05
        user.coins += 250


def inflation_control(user):
    if user.coins > 50000:
        user.coins = int(user.coins * 0.98)
