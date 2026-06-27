import random


def reward(user):
    user.xp += random.randint(8, 15)
    user.coins += random.randint(5, 12)
    user.qi += random.randint(1, 3)


def level_up(user):
    while user.xp >= user.level * 120:
        user.xp -= user.level * 120
        user.level += 1
        user.luck += 0.03
        user.coins += 25


def inflation_control(user):
    if user.coins > 50000:
        user.coins = int(user.coins * 0.98)
