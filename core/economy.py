import random


def reward(user):

    xp = random.randint(8, 10)

    coins = random.randint(3, 8)

    qi = random.randint(8, 15)

    user.xp += xp

    user.coins += coins

    user.qi += qi

    return coins


def level_up(user):
    while user.xp >= user.level * 500:
        user.xp -= user.level * 500
        user.level += 1
        user.luck += 0.05
        user.coins += 250


def inflation_control(user):
    if user.coins > 5000000:
        user.coins = int(user.coins * 0.98)
