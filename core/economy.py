import random


def reward():
    """
    基础聊天奖励

    不直接修改玩家数据。
    所有倍率统一在 chat() 中处理。

    返回：
    coins  基础金币
    xp     基础经验
    qi     基础灵气
    """

    return {
        "coins": random.randint(3, 8),
        "xp": random.randint(8, 10),
        "qi": random.randint(8, 15),
    }


def level_up(user):
    """
    玩家升级
    """

    while user.xp >= user.level * 500:

        user.xp -= user.level * 500

        user.level += 1

        # 升级增加个人幸运
        user.luck += 0.05

        # 升级奖励金币
        user.coins += 250



def inflation_control(user):
    """
    金币通胀控制
    """

    if user.coins > 5000000:
        user.coins = int(user.coins * 0.98)
