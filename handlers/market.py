import time
import random   # ⭐ 新增：用于行情波动

from telegram import Update
from telegram.ext import ContextTypes

from database import get_session
from models import User, Card, Market
from services.user_service import get_user


# ======================
# 🟢 挂单出售
# ======================
async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        card_id = int(context.args[0])
        price = int(context.args[1])
        amount = int(context.args[2])
    except:
        await update.message.reply_text("用法：/sell 卡ID 价格 数量")
        return

    with get_session() as s:
        u = get_user(s, update.effective_user.id, update.effective_user.username)

        cards_dict = dict(u.cards or {})
        cid_str = str(card_id)

        if cid_str not in cards_dict or cards_dict[cid_str] < amount:
            await update.message.reply_text("❌ 卡牌数量不足")
            return

        # 扣卡
        cards_dict[cid_str] -= amount
        if cards_dict[cid_str] <= 0:
            del cards_dict[cid_str]

        u.cards = cards_dict

        # 创建挂单
        listing = Market(
            seller_id=u.user_id,
            card_id=card_id,
            price=price,
            amount=amount,
            created_at=int(time.time())
        )

        s.add(listing)

        s.commit()

    await update.message.reply_text("✅ 挂单成功！")


# ======================
# 🟢 查看市场
# ======================
async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ⭐ 新增：轻量行情刷新（不会影响交易逻辑）
    update_card_market()

    with get_session() as s:
        listings = s.query(Market).order_by(Market.id.desc()).limit(10).all()

        if not listings:
            await update.message.reply_text("🛒 当前市场空空如也")
            return

        text = "🛒 当前交易市场（最新10条）：\n\n"

        for l in listings:
            card = s.get(Card, l.card_id)
            text += f"ID:{l.id} | {card.name if card else '未知'} | {l.amount}个 | {l.price}币\n"

        await update.message.reply_text(text)


# ======================
# 🟢 买入
# ======================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        listing_id = int(context.args[0])
    except:
        await update.message.reply_text("用法：/buy 挂单ID")
        return

    with get_session() as s:
        listing = s.get(Market, listing_id)
        if not listing:
            await update.message.reply_text("❌ 挂单不存在")
            return

        buyer = get_user(s, update.effective_user.id, update.effective_user.username)
        total_price = listing.price * listing.amount

        if buyer.coins < total_price:
            await update.message.reply_text("❌ 金币不足")
            return

        seller = s.get(User, listing.seller_id)

        # 扣钱 + 给卖家
        buyer.coins -= total_price
        fee = int(total_price * 0.1)
        if seller:
            seller.coins += total_price - fee

        # 给买家卡牌
        buyer.cards = buyer.cards or {}
        cid = str(listing.card_id)
        buyer.cards[cid] = buyer.cards.get(cid, 0) + listing.amount

        s.delete(listing)

        s.commit()

    await update.message.reply_text(f"✅ 购买成功！花费 {total_price} 金币")


# ======================
# 🟢 我的挂单
# ======================
async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):

    with get_session() as s:
        uid = update.effective_user.id
        orders = s.query(Market).filter(Market.seller_id == uid).all()

        if not orders:
            await update.message.reply_text("你当前没有挂单")
            return

        text = "📦 你的挂单：\n\n"

        for o in orders:
            card = s.get(Card, o.card_id)
            text += f"ID:{o.id} | {card.name if card else '未知'} | {o.amount}个 | {o.price}币\n"

        await update.message.reply_text(text)


# =========================================================
# 📊 ⭐ 新增：卡牌行情系统（核心）
# =========================================================

def update_card_market():
    """
    ⭐ 轻量行情系统（不会影响交易）
    - 随机波动卡牌价格
    - 只用于 /market 显示
    """

    with get_session() as s:
        cards = s.query(Card).all()

        for c in cards:
            if not hasattr(c, "min_price") or not hasattr(c, "max_price"):
                continue

            old = c.price

            # NR波动大
            if c.rarity == "NR":
                new = random.randint(c.min_price, c.max_price)
                new = int(old * 0.4 + new * 0.6)

            # SSR/SR中等波动
            elif c.rarity in ["SSR", "SR"]:
                new = random.randint(c.min_price, c.max_price)
                new = int(old * 0.5 + new * 0.5)

            # N/R稳定
            else:
                new = random.randint(c.min_price, c.max_price)
                new = int(old * 0.7 + new * 0.3)

            c.last_price = old
            c.price = max(1, new)

            if old > 0:
                c.change = round(((new - old) / old) * 100, 2)

        s.commit()
