import random
import time
from models import Card

# =========================
# 1️⃣ 冷却控制
# =========================

def can_drop(user):
    """70秒冷却"""
    return int(time.time()) - user.last_drop > 70


# =========================
# 2️⃣ 掉卡概率（保留你的原逻辑）
# =========================

def drop_rate(user):
    """整体掉卡概率（不改）"""
    return min(0.80, 0.05 + user.luck * 0.50)


# =========================
# 3️⃣ 稀有度权重系统
# =========================

def get_card_by_rarity(cards_list):
    """按稀有度加权抽卡"""
    if not cards_list:
        return None

    weights = []
    for card in cards_list:
        if card.rarity == "N":
            weights.append(100)
        elif card.rarity == "R":
            weights.append(40)
        elif card.rarity == "SR":
            weights.append(12)
        elif card.rarity == "SSR":
            weights.append(3)
        elif card.rarity == "UR":
            weights.append(0.8)
        else:
            weights.append(10)

    return random.choices(cards_list, weights=weights, k=1)[0]


# =========================
# 4️⃣ 获取可用卡池（关键修复）
# =========================

def get_available_cards(session):
    """只返回还有库存的卡"""
    return session.query(Card).filter(Card.remain > 0).all()


# =========================
# 5️⃣ 核心掉卡入口（必须用这个）
# =========================

def try_drop(session, user):
    """
    ⭐ 唯一掉卡入口函数
    chat / event / reward 都必须调用它
    """

    now = int(time.time())

    # ❌ 冷却
    if not can_drop(user):
        return None

    # ❌ 概率判定
    if random.random() > drop_rate(user):
        return None

    # ❌ 卡池检查
    cards_list = get_available_cards(session)
    if not cards_list:
        return None

    # 🎯 抽卡
    card = get_card_by_rarity(cards_list)
    if not card:
        return None

    # ❗库存扣减（核心修复）
    if card.remain <= 0:
        return None

    card.remain -= 1

    # 🎴 发给玩家
    user.cards = user.cards or {}
    cid = str(card.id)
    user.cards[cid] = user.cards.get(cid, 0) + 1

    # ⏱ 更新冷却
    user.last_drop = now

    return card
