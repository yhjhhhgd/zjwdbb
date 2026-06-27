import time
from telegram import Update
from telegram.ext import ContextTypes

from ..database import Session
from ..models import User, Card, Market
from ..services.user_service import get_user


# =========================
# 📦 挂单出售卡牌
# =========================
async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        card_id = int(context.args[0])
        price = int(context.args[1])
        amount = int(context.args[2])
    except:
        await update.message.reply_text("用法：/sell 卡ID 价格 数量")
        return

    if price <= 0 or amount <= 0:
        await update.message.reply_text("参数错误")
        return

    s = Session()
    u = get_user(s, update.effective_user.id, update.effective_user.username)

    cards = u.cards or {}

    if str(card_id) not in cards or cards[str(card_id)] < amount:
        await update.message.reply_text("❌ 卡牌不足")
        s.close()
        return

    # 扣卡
    cards[str(card_id)] -= amount
    if cards[str(card_id)] <= 0:
        del cards[str(card_id)]

    u.cards = cards

    listing = Market(
        seller_id=u.user_id,
        card_id=card_id,
        price=price,
        amount=amount,
        created_at=int(time.time())
    )

    s.add(listing)
    s.commit()
    s.close()

    await update.message.reply_text(
        f"✅ 挂单成功\n卡ID:{card_id}\n数量:{amount}\n价格:{price}"
    )


# =========================
# 🛒 市场列表
# =========================
async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = Session()

    listings = s.query(Market).order_by(Market.id.desc()).limit(10).all()

    if not listings:
        await update.message.reply_text("🛒 市场空空如也")
        s.close()
        return

    text = "🛒 当前交易市场：\n\n"

    for l in listings:
        card = s.get(Card, l.card_id)
        text += (
            f"ID:{l.id}\n"
            f"卡牌:{card.name if card else '未知'}\n"
            f"数量:{l.amount}\n"
            f"价格:{l.price}\n"
            f"-------------------\n"
        )

    s.close()
    await update.message.reply_text(text)


# =========================
# 💰 购买卡牌
# =========================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        listing_id = int(context.args[0])
    except:
        await update.message.reply_text("用法：/buy 挂单ID")
        return

    s = Session()

    listing = s.get(Market, listing_id)

    if not listing:
        await update.message.reply_text("❌ 挂单不存在")
        s.close()
        return

    buyer = get_user(s, update.effective_user.id, update.effective_user.username)

    total_price = listing.price * listing.amount

    if buyer.coins < total_price:
        await update.message.reply_text("❌ 灵币不足")
        s.close()
        return

    seller = s.get(User, listing.seller_id)

    # 扣钱
    buyer.coins -= total_price

    # 分钱（10%手续费）
    fee = int(total_price * 0.1)
    seller.coins += total_price - fee if seller else 0

    # 给卡
    buyer_cards = buyer.cards or {}
    buyer_cards[str(listing.card_id)] = buyer_cards.get(str(listing.card_id), 0) + listing.amount
    buyer.cards = buyer_cards

    # 删除挂单
    s.delete(listing)

    s.commit()
    s.close()

    await update.message.reply_text(
        f"✅ 购买成功\n花费:{total_price}\n获得卡ID:{listing.card_id}"
    )


# =========================
# 📦 查看我的挂单
# =========================
async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = Session()

    uid = update.effective_user.id

    orders = s.query(Market).filter(Market.seller_id == uid).all()

    if not orders:
        await update.message.reply_text("你没有挂单")
        s.close()
        return

    text = "📦 你的挂单：\n\n"

    for o in orders:
        card = s.get(Card, o.card_id)
        text += (
            f"ID:{o.id} | {card.name if card else '未知'} | "
            f"{o.amount}个 | {o.price}币\n"
        )

    s.close()
    await update.message.reply_text(text)
