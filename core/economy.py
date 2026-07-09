import random


def reward():
    """
    基础聊天奖励（不直接修改玩家属性）
    所有奖励统一交给 chat() 处理，
    方便宗门、VIP、活动等倍率统一计算。
    """
    return {
        "coins": random.randint(3, 8),
        "xp": random.randint(8, 10),
        "qi": random.randint(8, 15),
    }


def level_up(user):
    while user.xp >= user.level * 500:
        user.xp -= user.level * 500
        user.level += 1
        user.luck += 0.05
        user.coins += 250  # 升级奖励保留


def inflation_control(user):
    if user.coins > 5000000:
        user.coins = int(user.coins * 0.98)
