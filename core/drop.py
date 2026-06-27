import random
import time


def can_drop(user):
    return int(time.time()) - user.last_drop > 70


def drop_rate(user):
    return min(0.22, 0.06 + user.luck * 0.02)
