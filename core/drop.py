import random
import time

def can_drop(user):
    """冷却时间：70秒"""
    return int(time.time()) - user.last_drop > 70


def drop_rate(user):
    """整体掉卡概率"""
    return min(0.38, 0.06 + user.luck * 0.10)   # 不改


def get_card_by_rarity(cards_list):
    """按稀有度加权随机掉卡（优化版）"""
    if not cards_list:
        return None

    weights = []
    for card in cards_list:
        if card.rarity == "N":
            weights.append(100)   # ↓ N 稍微压低集中度
        elif card.rarity == "R":
            weights.append(40)
        elif card.rarity == "SR":
            weights.append(12)
        elif card.rarity == "SSR":
            weights.append(3)
        elif card.rarity == "UR":
            weights.append(0.8)   # ⭐ UR 提升一点点存在感
        else:
            weights.append(10)

    return random.choices(cards_list, weights=weights, k=1)[0]
