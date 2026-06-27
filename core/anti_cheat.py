import time


def check_message(user):
    now = int(time.time())

    if user.frozen:
        return False, now

    if now - user.last_msg < 4:
        return False, now

    user.last_msg = now
    return True, now
