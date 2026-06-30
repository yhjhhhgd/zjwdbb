import random
import time

def can_drop(user):
    """冷却时间：70秒"""
    return int(time.time()) - user.last_drop > 70


def drop_rate(user):
    """整体掉卡概率"""
    return min(0.30, 0.12 + user.luck * 0.03)   # 可自行调整


def get_card_by_rarity(cards_list):
    """按稀有度加权随机掉卡"""
    if not cards_list:
        return None
    
    # 按稀有度设置权重（数值越高越容易掉）
    weights = []
    for card in cards_list:
        if card.rarity == "N":
            weights.append(60)
        elif card.rarity == "R":
            weights.append(25)
        elif card.rarity == "SR":
            weights.append(10)
        elif card.rarity == "SSR":
            weights.append(4)
        elif card.rarity == "UR":
            weights.append(1)
        else:
            weights.append(10)
    
    return random.choices(cards_list, weights=weights, k=1)[0]
