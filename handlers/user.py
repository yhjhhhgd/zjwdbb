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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎴 V4经济系统已启动")


async def my(update: Update, context):
    s = Session()
    u = get_user(s, update.effective_user.id, update.effective_user.username)

    await update.message.reply_text(
        f"""📊 玩家状态
Lv:{u.level}
💰{u.coins}
🍀{u.luck:.2f}
🎴卡:{len(u.cards or {})}
"""
    )
    s.close()


async def chat(update: Update, context):
    s = Session()
    u = get_user(s, update.effective_user.id, update.effective_user.username)

    ok, _ = check_message(u)
    if not ok:
        s.close()
        return

    reward(u)
    level_up(u)
    inflation_control(u)

    if random.random() < 0.05:
        event, val = random_event()
        u.coins += val
        await update.message.reply_text(f"🌍 事件：{event} ({val})")

    if can_drop(u) and random.random() < drop_rate(u):
        card = s.query(Card).first()
        if card:
            u.cards = u.cards or {}
            cid = str(card.id)
            u.cards[cid] = u.cards.get(cid, 0) + 1
            u.last_drop = int(time.time())

            await update.message.reply_text(f"🎉 掉落：{card.name}")

    s.commit()
    s.close()
