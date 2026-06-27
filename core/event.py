import random

EVENTS = [
    ("财神降临", 50),
    ("经济波动", -20),
    ("幸运爆发", 35),
    ("盗贼袭击", -15),
    ("神秘奖励", 80)
]


def random_event():
    return random.choice(EVENTS)
