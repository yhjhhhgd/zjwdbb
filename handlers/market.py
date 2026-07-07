import time   # ← 新增这一行
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_session
from models import User, Card
from services.user_service import get_user
from services.market_service import get_card_price, get_all_cards


async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示第一页行情 + 按钮"""
    with get_session() as s:
        cards = get_all_cards(s)
        await send_market_page(update, cards, page=1)


async def market_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """按钮翻页回调"""
    query = update.callback_query
    await query.answer()

    try:
        page = int(query.data.split("_")[1])
    except:
        page = 1

    with get_session() as s:
        cards = get_all_cards(s)
        await send_market_page(update, cards, page, edit=True)


async def send_market_page(update, cards, page=1, edit=False):
    """统一发送/编辑分页消息"""
    page_size = 8
    total_pages = (len(cards) + page_size - 1) // page_size
    page = max(1, min(page, total_pages))

    start = (page - 1) * page_size
    end = start + page_size
    page_cards = cards[start:end]

    text = f"📊 **生肖卡牌行情** 第 {page}/{total_pages} 页\n\n"
    
    for card in page_cards:
        price = get_card_price(card.name)
        text += f"🆔 ID: {card.id} | 🃏 {card.name} | 💰 `{price:,}` | 剩余 `{card.remain}` | ⭐{card.rarity}\n"

    text += "\n💡 使用下方按钮翻页"

    # 创建按钮
    keyboard = []
    row = []
    if page > 1:
        row.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"market_{page-1}"))
    if page < total_pages:
        row.append(InlineKeyboardButton("下一页 ➡️", callback_data=f"market_{page+1}"))
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    if edit:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


# ====================== 买卖功能 ======================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """从系统购买"""
    if not context.args:
        await update.message.reply_text("用法: /buy <卡ID> <数量>")
        return

    try:
        card_id = int(context.args[0])
        amount = int(context.args[1]) if len(context.args) > 1 else 1
    except:
        await update.message.reply_text("参数错误！")
        return

    with get_session() as s:
        user = get_user(s, update.effective_user.id, update.effective_user.username)
        
        # === 冷却检查 ===
        now = int(time.time())
        if now - getattr(user, 'last_market_action', 0) < 30:
            await update.message.reply_text("⏳ 操作太频繁，请 30 秒后再试！")
            return
        user.last_market_action = now

        card = s.get(Card, card_id)
        if not card or card.remain < amount:
            await update.message.reply_text("❌ 库存不足或卡牌不存在")
            return

        price = get_card_price(card.name)
        total = price * amount
        fee = int(total * 0.08)          # 8% 手续费
        total_with_fee = total + fee

        if user.coins < total_with_fee:
            await update.message.reply_text(f"❌ 金币不足，需要 {total_with_fee:,} 金币（含手续费）")
            return

        user.coins -= total_with_fee
        card.remain -= amount

        user.cards = user.cards or {}
        cid = str(card_id)
        user.cards[cid] = user.cards.get(cid, 0) + amount

        await update.message.reply_text(f"✅ 购买成功！花费 {total_with_fee:,} 金币（含8%手续费）")
        s.commit()


async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """卖给系统"""
    if not context.args:
        await update.message.reply_text("用法: /sell <卡ID> <数量>")
        return

    try:
        card_id = int(context.args[0])
        amount = int(context.args[1]) if len(context.args) > 1 else 1
    except:
        await update.message.reply_text("参数错误！")
        return

    with get_session() as s:
        user = get_user(s, update.effective_user.id, update.effective_user.username)
        
        # === 冷却检查 ===
        now = int(time.time())
        if now - getattr(user, 'last_market_action', 0) < 30:
            await update.message.reply_text("⏳ 操作太频繁，请 30 秒后再试！")
            return
        user.last_market_action = now

        card = s.get(Card, card_id)
        if not card or user.cards.get(str(card_id), 0) < amount:
            await update.message.reply_text("❌ 你没有足够数量的这张卡")
            return

        price = get_card_price(card.name)
        total = price * amount
        fee = int(total * 0.08)          # 8% 手续费
        total_after_fee = total - fee

        user.cards[str(card_id)] -= amount
        if user.cards[str(card_id)] <= 0:
            del user.cards[str(card_id)]

        user.coins += total_after_fee
        card.remain += amount

        await update.message.reply_text(f"✅ 卖出成功！获得 {total_after_fee:,} 金币（已扣8%手续费）")
        s.commit()
