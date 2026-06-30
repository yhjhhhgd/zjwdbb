import random
import time


def can_drop(user):
    return int(time.time()) - user.last_drop > 70


def drop_rate(user):
    return 0.8   # 80%概率（测试用，后面记得改回来）
