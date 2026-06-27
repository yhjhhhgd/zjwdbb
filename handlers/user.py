import random
import time
from telegram import Update
from telegram.ext import ContextTypes

from database import Session
from models import User, Card

from services.user_service import get_user
from core.economy import reward, level_up, inflation_control
from core.anti_cheat import check_message
from core.drop import can_drop, drop_rate
from core.event import random_event


# ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎴 可达鸭养成卡牌启动")


# ===================== MY INFO =====================
async def my(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = Session()

    u = get_user(
        s,
        update.effective_user.id,
        update.effective_user.username
    )

    await update.message.reply_text(
        f"""📊 玩家状态

👤 等级: {u.level}
💰 金币: {u.coins}
🍀 幸运: {u.luck:.2f}
⚡ 灵气: {u.qi}
🎴 卡牌数量: {len(u.cards or {})}
"""
    )

    s.close()


# ===================== CARDS (你缺的核心功能) =====================
async def cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = Session()

    u = get_user(
        s,
        update.effective_user.id,
        update.effective_user.username
    )

    if not u.cards:
        await update.message.reply_text("🎴 你还没有卡牌，快去聊天获取掉落吧！")
        s.close()
        return

    text = "🎴 你的卡牌收藏：\n\n"

    for cid, amount in u.cards.items():
        try:
            card = s.get(Card, int(cid))
        except:
            continue

        if card:
            text += (
                f"🃏 {card.name}\n"
                f"⭐ 稀有度: {card.rarity}\n"
                f"📦 数量: {amount}\n\n"
            )

    await update.message.reply_text(text)
    s.close()


# ===================== CHAT CORE =====================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = Session()

    u = get_user(
        s,
        update.effective_user.id,
        update.effective_user.username
    )

    ok, _ = check_message(u)
    if not ok:
        s.close()
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

    # ===================== 掉卡系统（已修复） =====================
    if can_drop(u) and random.random() < drop_rate(u):

        cards = s.query(Card).all()   # ✅ 修复：不再只 first()

        if cards:
            card = random.choice(cards)  # ✅ 真随机掉卡

            u.cards = u.cards or {}
            cid = str(card.id)

            u.cards[cid] = u.cards.get(cid, 0) + 1
            u.last_drop = int(time.time())

            await update.message.reply_text(f"🎉 掉落卡牌：{card.name} ⭐{card.rarity}")

    s.commit()
    s.close()
