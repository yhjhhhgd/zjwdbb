from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from database import get_session
from models import User, SpiritTicket, ShopItem, UsedItemLog
import time

DEFAULT_ITEMS = [
    {"name": "红包雨", "price": 100, "description": "全群随机红包", "reward_type": "redpacket", "reward_value": "500"},
    {"name": "金币大礼包", "price": 50, "description": "立即获得10000金币", "reward_type": "coins", "reward_value": "10000"},
    {"name": "幸运祝福", "price": 80, "description": "幸运值+0.5（24小时）", "reward_type": "buff", "reward_value": "luck"},
    {"name": "称号【修仙达人】", "price": 200, "description": "获得专属称号", "reward_type": "title", "reward_value": "修仙达人"},
]

async def exchange_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with get_session() as s:
        user = s.get(User, user_id)
        if not user or user.qi < 10000:
            await update.message.reply_text("❌ 灵气不足！最低兑换10000灵气。")
            return
        amount = user.qi // 10000
        ticket = s.get(SpiritTicket, user_id) or SpiritTicket(user_id=user_id, amount=0)
        ticket.amount += amount
        user.qi -= amount * 10000
        s.add(ticket)
        s.commit()
        await update.message.reply_text(f"✅ 兑换成功！获得 {amount} 张灵票\n当前灵票：{ticket.amount}")

async def spirit_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_shop_page(update, context, page=0)

async def show_shop_page(update, context, page=0):
    with get_session() as s:
        items = s.query(ShopItem).all()
        if not items:
            for data in DEFAULT_ITEMS:
                s.add(ShopItem(**data))
            s.commit()
            items = s.query(ShopItem).all()
        
        start = page * 5
        page_items = items[start:start+5]
        
        keyboard = []
        for item in page_items:
            keyboard.append([InlineKeyboardButton(f"{item.name} - {item.price}票", callback_data=f"buy_{item.id}")])
        
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("上一页", callback_data=f"shop_{page-1}"))
        if start + 5 < len(items):
            nav.append(InlineKeyboardButton("下一页", callback_data=f"shop_{page+1}"))
        keyboard.append(nav)
        
        text = "🛒 **灵气商店**\n\n" + "\n".join([f"• {item.name} | {item.price}票 | {item.description}" for item in page_items])
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def my_bag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with get_session() as s:
        logs = s.query(UsedItemLog).filter_by(user_id=user_id).order_by(UsedItemLog.used_at.desc()).limit(10).all()
        if not logs:
            await update.message.reply_text("🎒 你的背包是空的。")
            return
        text = "🎒 **你的背包**\n\n" + "\n".join([f"• {log.item_name} (已使用)" for log in logs])
        await update.message.reply_text(text)

async def shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    if data.startswith("shop_"):
        page = int(data.split("_")[1])
        await show_shop_page(query, context, page)
        return
    
    if data.startswith("buy_"):
        item_id = int(data.split("_")[1])
        with get_session() as s:
            ticket = s.get(SpiritTicket, user_id)
            if not ticket or ticket.amount <= 0:
                await query.edit_message_text("❌ 灵票不足！")
                return
            item = s.get(ShopItem, item_id)
            if not item or ticket.amount < item.price:
                await query.edit_message_text("❌ 灵票不足，无法购买！")
                return
            ticket.amount -= item.price
            log = UsedItemLog(user_id=user_id, item_name=item.name)
            s.add(log)
            s.commit()
            await query.edit_message_text(f"✅ 购买成功！\n商品：{item.name}\n消耗：{item.price}灵票\n剩余灵票：{ticket.amount}\n\n请联系管理员发放奖励。")

async def used_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """管理员查看使用记录"""
    with get_session() as s:
        logs = s.query(UsedItemLog).order_by(UsedItemLog.used_at.desc()).limit(20).all()
        if not logs:
            await update.message.reply_text("暂无使用记录。")
            return
        text = "📋 **最近使用记录**\n\n" + "\n".join([
            f"用户 {log.user_id} 使用了 {log.item_name}" for log in logs
        ])
        await update.message.reply_text(text)

def register_spirit_handlers(app):
    app.add_handler(CommandHandler("exchangeticket", exchange_ticket))
    app.add_handler(CommandHandler("shop", spirit_shop))
    app.add_handler(CommandHandler("bag", my_bag))
    app.add_handler(CommandHandler("used_items", used_items))
    app.add_handler(CallbackQueryHandler(shop_callback, pattern="^(shop_|buy_)"))
