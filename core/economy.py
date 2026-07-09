import random


def reward(user):
    """
    基础聊天奖励
    这里只增加经验和灵气，金币返回给 chat() 统一处理，
    方便宗门/VIP/活动等倍率统一计算。
    """
    xp = random.randint(8, 10)
    coins = random.randint(3, 8)
    qi = random.randint(8, 15)

    user.xp += xp
    user.qi += qi

    return coins


def level_up(user):
    while user.xp >= user.level * 500:
        user.xp -= user.level * 500
        user.level += 1
        user.luck += 0.05
        user.coins += 250  # 升级奖励保留


def inflation_control(user):
    if user.coins > 5000000:
        user.coins = int(user.coins * 0.98)
