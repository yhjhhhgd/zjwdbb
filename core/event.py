import random

EVENTS = [
    ("财神降临", 80),
    ("天降灵气", 60),
    ("幸运爆发", 45),
    ("神秘宝箱", 666),
    ("经济波动", -300),
    ("盗贼袭击", -205),
    ("市场崩盘", -500),
    ("幸运祝福", 55),
    ("灵兽馈赠", 70),
]


def random_event():
    return random.choice(EVENTS)


def apply_event(user, event_name, value):
    """应用随机事件（安全版）"""

    # ✅ 统一字段修复
    if not hasattr(user, "coins") or user.coins is None:
        user.coins = 0

    if value >= 0:
        user.coins += value
        return f"🌍 {event_name} +{value}💰"

    # 负收益处理
    deduct = min(abs(value), user.coins)

    # ❗ 防止 -0 显示
    if deduct <= 0:
        return f"🌍 {event_name} 但你没有金币损失"

    user.coins -= deduct

    return f"🌍 {event_name} -{deduct}💰"
