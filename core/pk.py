import random
import time


def get_pk_limit(user):
    now = int(time.time())
    today = now // 86400

    if user.last_pk_date != today:
        user.pk_count_today = 0
        user.last_pk_date = today

    if user.pk_count_today >= 3:
        return False, "⏳ 你今天已经进行了3次PK，明日再战吧！"

    return True, ""


def calculate_win_rate(attacker_power, defender_power):
    diff = attacker_power - defender_power
    rate = 50 + diff * 0.8
    return max(12, min(88, rate))


def get_win_text(attacker_card, defender_card):
    texts = [
        f"⚔️ {attacker_card.name} 剑光如虹，直破敌阵！",
        f"🔥 {attacker_card.name} 强势碾压，{defender_card.name} 溃不成军！",
        f"🐉 龙威浩荡，{attacker_card.name} 一战封神！",
        f"🌟 天降神力，{attacker_card.name} 所向披靡！"
    ]
    return random.choice(texts)


def get_lose_text(attacker_card, defender_card):
    texts = [
        f"惜败一筹！{attacker_card.name} 虽勇，仍败于{defender_card.name}之手。",
        f"棋差一招，{attacker_card.name} 憾败而归。",
        f"{defender_card.name} 技高一筹，{attacker_card.name} 含恨退场。"
    ]
    return random.choice(texts)


# =========================
# ⭐ 新增：PK金币消耗（重点）
# =========================
def calculate_pk_cost(user, card):
    """
    金币消耗 = 卡牌强度 × 7
    灵气不变（保持原逻辑）
    """

    qi_cost = 520  # 不变

    power = getattr(card, "power", 0)
    coin_cost = power * 7

    return qi_cost, coin_cost


def check_pk_cost(user, qi_cost, coin_cost):
    if user.qi < qi_cost or user.coins < coin_cost:
        return False, f"灵气或金币不足（需{qi_cost}灵气 + {coin_cost}金币）"
    return True, ""
