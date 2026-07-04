import random

EVENTS = [
    ("财神降临", 80),
    ("天降灵气", 60),
    ("幸运爆发", 45),
    ("神秘宝箱", 666),
    ("经济波动", -30),
    ("盗贼袭击", -25),
    ("市场崩盘", -500),
    ("幸运祝福", 55),
    ("灵兽馈赠", 70),
]


def random_event():
    return random.choice(EVENTS)


def apply_event(user, event_name, value):
    """应用随机事件（安全版）"""

    # 保底字段
    if not hasattr(user, "coin") or user.coin is None:
        user.coin = 0

    if value >= 0:
        user.coin += value
        return f"🌍 {event_name} +{value}💰"

    # 负收益处理
    deduct = min(abs(value), user.coin)
    user.coin -= deduct

    return f"🌍 {event_name} -{deduct}💰"
