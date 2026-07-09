import random
import time
import logging
from telegram import Update
from telegram.ext import ContextTypes

from database import get_session
from models import User, Card, get_realm_name
from services.user_service import get_user
from core.economy import reward, level_up, inflation_control
from core.anti_cheat import check_message
from core.drop import try_drop
from core.event import random_event, apply_event
from handlers.invite import track_chat_logic

# 新增宗门相关导入
from handlers.sect import handle_sect_message, apply_sect_tax


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎴 可达鸭养成卡牌启动")


async def my(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_session() as s:
        u = get_user(s, update.effective_user.id, update.effective_user.username)
        realm_name = get_realm_name(u.level)

        await update.message.reply_text(
            f"""📊 玩家信息

🌀 境界: {realm_name} (第 {u.level} 层)
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

        for cid, amount in (u.cards or {}).items():
            try:
                card = s.get(Card, int(cid))
                if not card:
                    continue

                text += (
                    f"🆔 ID: {card.id}\n"
                    f"🃏 {card.name}\n"
                    f"⭐ 稀有度: {card.rarity}\n"
                    f"📦 数量: {amount}\n\n"
                )
            except Exception as e:
                print("CARD DISPLAY ERROR:", cid, e)
                continue

        await update.message.reply_text(text)


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 宗门对话
    if await handle_sect_message(update, context):
        return

    with get_session() as s:
        u = get_user(s, update.effective_user.id, update.effective_user.username)

        # 反作弊
        ok, _ = check_message(u)
        if not ok:
            return

        # ===================== 宗门加成 =====================
        from handlers.sect import apply_sect_bonus
        coin_mult, exp_mult, qi_mult, luck_mult = apply_sect_bonus(u)

        # ===================== 基础收益（只对本次收益加成） =====================
        reward_amount = reward(u) or 0
        reward_amount = int(reward_amount * coin_mult)   # 只对本次收益加成

        # ===================== 宗门抽成 + 贡献度 =====================
        final_amount = await apply_sect_tax(s, u, reward_amount)

        # ===================== 其他系统 =====================
        level_up(u)
        inflation_control(u)

        # ===================== 邀请系统 =====================
        reward_data = track_chat_logic(s, u)
        if reward_data:
            await context.bot.send_message(
                chat_id=reward_data["inviter_id"],
                text=reward_data["text"]
            )
            await update.message.reply_text("🎉 有人完成有效邀请！")

        # ===================== 事件 =====================
        if random.random() < 0.30:
            if random.random() < 0.26:
                event_name, value = random_event()
                message = apply_event(u, event_name, value)
                await update.message.reply_text(message)
