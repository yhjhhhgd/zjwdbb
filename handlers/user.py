import random
import time
from telegram import Update
from telegram.ext import ContextTypes

from database import get_session
from models import User, Card
from services.user_service import get_user
from core.economy import reward, level_up, inflation_control
from core.anti_cheat import check_message
from core.drop import can_drop, drop_rate
from core.event import random_event


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎴 可达鸭养成卡牌启动")


async def my(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_session() as s:
        u = get_user(s, update.effective_user.id, update.effective_user.username)
        await update.message.reply_text(
            f"""📊 玩家状态

👤 等级: {u.level}
💰 金币: {u.coins}
🍀 幸运: {u.luck:.2f}
⚡ 灵气: {u.qi}
🎴 卡牌数量: {len(u.cards or {})}
"""
        )


async def cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_session() as s:
        u = get_user(s, update.effective_user.id, update.effective_user.username)
        
        if not u.cards:
            await update.message.reply_text("🎴 你还没有卡牌，快去群里聊天获取掉落吧！")
            return

        text = "🎴 你的卡牌收藏（ID请用于卖卡）：\n\n"
        for cid, amount in u.cards.items():
            card = s.get(Card, int(cid))
            if card:
                text += (
                    f"🆔 **ID: {card.id}**\n"
                    f"🃏 {card.name}\n"
                    f"⭐ 稀有度: {card.rarity}\n"
                    f"📦 数量: {amount}\n\n"
                )
        
        await update.message.reply_text(text)


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_session() as s:
        u = get_user(s, update.effective_user.id, update.effective_user.username)

        # 反作弊检查
        ok, _ = check_message(u)
        if not ok:
            return

        # 基础收益
        reward(u)
        level_up(u)
        inflation_control(u)

        # 随机事件
        if random.random() < 0.05:
            event, val = random_event()
            u.coins += val
            await update.message.reply_text(f"🌍 事件触发：{event} ({val}💰)")

        # ===================== 掉卡系统 =====================
        if can_drop(u) and random.random() < drop_rate(u):
            cards_list = s.query(Card).all()
            
            if cards_list:
                card = random.choice(cards_list)
                
                u.cards = u.cards or {}
                cid = str(card.id)
                
                u.cards[cid] = u.cards.get(cid, 0) + 1
                u.last_drop = int(time.time())

                await update.message.reply_text(
                    f"🎉 掉落卡牌：{card.name} ⭐{card.rarity}"
                )

        # 提交所有更改
        # (with get_session 会自动 commit)
