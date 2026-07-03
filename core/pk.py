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
