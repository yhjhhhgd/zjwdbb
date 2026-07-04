import random
import time

from models import Card
from database import get_session


# =====================================================
# 📊 1️⃣ 主行情更新函数（核心）
# =====================================================
def update_market_prices():
    """
    更新所有卡牌价格（生肖 + NR + 普通卡）
    可由定时任务 / /market触发
    """

    with get_session() as session:
        cards = session.query(Card).all()

        for c in cards:
            if not hasattr(c, "min_price") or not hasattr(c, "max_price"):
                continue

            old_price = c.price or 1

            # ======================
            # 🟡 NR（高波动）
            # ======================
            if c.rarity == "NR":
                new_price = random.randint(c.min_price, c.max_price)
                new_price = int(old_price * 0.35 + new_price * 0.65)

            # ======================
            # 🟣 SSR / SR（中波动）
            # ======================
            elif c.rarity in ["SSR", "SR"]:
                new_price = random.randint(c.min_price, c.max_price)
                new_price = int(old_price * 0.5 + new_price * 0.5)

            # ======================
            # 🟢 N / R（低波动）
            # ======================
            else:
                new_price = random.randint(c.min_price, c.max_price)
                new_price = int(old_price * 0.7 + new_price * 0.3)

            # 防止异常
            new_price = max(1, new_price)

            # 涨跌幅
            if old_price > 0:
                c.change = round(((new_price - old_price) / old_price) * 100, 2)
            else:
                c.change = 0

            c.last_price = old_price
            c.price = new_price

        session.commit()


# =====================================================
# 📊 2️⃣ 生肖行情汇总（给 /行情 用）
# =====================================================
def get_zodiac_overview():
    """
    返回：12生肖 + NR 的平均涨跌
    """

    with get_session() as session:
        cards = session.query(Card).all()

        zodiac_map = {}
        nr_list = []

        for c in cards:
            if c.rarity == "NR":
                nr_list.append(c)
                continue

            zodiac_map.setdefault(c.zodiac, []).append(c)

        result = []

        # ======================
        # 🟡 生肖平均行情
        # ======================
        for zodiac, items in zodiac_map.items():
            avg_change = sum(i.change or 0 for i in items) / len(items)

            result.append({
                "name": zodiac,
                "change": round(avg_change, 2)
            })

        # ======================
        # 🔴 NR 独立行情
        # ======================
        if nr_list:
            avg_nr = sum(i.change or 0 for i in nr_list) / len(nr_list)

            result.append({
                "name": "NR",
                "change": round(avg_nr, 2)
            })

        return result


# =====================================================
# 📊 3️⃣ 单生肖行情（/行情 鼠）
# =====================================================
def get_zodiac_detail(zodiac: str):
    """
    返回某个生肖下所有卡牌行情
    """

    with get_session() as session:
        cards = session.query(Card).filter(Card.zodiac == zodiac).all()

        if not cards:
            return None

        return [
            {
                "name": c.name,
                "price": c.price,
                "change": c.change,
                "power": c.power,
                "rarity": c.rarity
            }
            for c in cards
        ]


# =====================================================
# 📊 4️⃣ 单卡行情查询（可选扩展）
# =====================================================
def get_card_detail(card_name: str):
    """
    查询单张卡行情
    """

    with get_session() as session:
        c = session.query(Card).filter(Card.name == card_name).first()

        if not c:
            return None

        return {
            "name": c.name,
            "price": c.price,
            "change": c.change,
            "power": c.power,
            "remain": c.remain,
            "rarity": c.rarity,
            "zodiac": c.zodiac
        }


# =====================================================
# 📊 5️⃣ 工具函数：安全价格计算
# =====================================================
def calc_price(old_price, min_p, max_p, weight=0.5):
    """
    通用价格计算工具
    """
    new_price = random.randint(min_p, max_p)
    new_price = int(old_price * (1 - weight) + new_price * weight)
    return max(1, new_price)
