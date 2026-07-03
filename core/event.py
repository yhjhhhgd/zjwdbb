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
    """应用事件并防止金币变成负数"""
    if value > 0:
        # 正收益直接增加
        user.coins += value
        return f"🌍 {event_name} (+{value}💰)"
    
    else:
        # 负收益时防止扣成负数
        actual_deduct = min(-value, user.coins)   # 最多扣到0
        user.coins -= actual_deduct
        return f"🌍 {event_name} (-{actual_deduct}💰)"
