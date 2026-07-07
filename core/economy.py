import random


def reward(user):
    user.xp += random.randint(8, 18)
    user.coins += random.randint(8, 20)
    user.qi += random.randint(8, 15)


def level_up(user):
    while user.xp >= user.level * 500:
        user.xp -= user.level * 500
        user.level += 1
        user.luck += 0.05
        user.coins += 250


def inflation_control(user):
    if user.coins > 500000:
        user.coins = int(user.coins * 0.98)
