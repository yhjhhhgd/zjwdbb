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
from models import SpiritTicket   # 添加这一行

# 新增宗门相关导入
from handlers.sect import handle_sect_message, apply_sect_tax, apply_sect_bonus

# =====================
# 只允许在这个群获得收益
# =====================
ALLOWED_GROUP_ID = -1003807963429   # ← 你的群ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎴 可达鸭养成卡牌启动")


async def my(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_session() as s:
        u = get_user(s, update.effective_user.id, update.effective_user.username)
        realm_name = get_realm_name(u.level)

        ticket = s.get(SpiritTicket, u.user_id)
        ticket_amount = ticket.amount if ticket else 0

        await update.message.reply_text(
            f"""📊 玩家信息

🌀 境界: {realm_name} (第 {u.level} 层)
💰 金币: {u.coins}
🍀 幸运: {u.luck:.2f}
⚡ 灵气: {u.qi}
🎟️ 灵票: {ticket_amount}
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
    # =====================
    # 限制只有指定群才能获得收益
    # =====================
    if update.effective_chat.id != ALLOWED_GROUP_ID:
        return  # 其他群直接跳过所有收益

    # =====================
    # 宗门创建对话处理
    # =====================
    if await handle_sect_message(update, context):
        return

    with get_session() as s:
        u = get_user(
            s,
            update.effective_user.id,
            update.effective_user.username
        )

        # =====================
        # 反作弊
        # =====================
        ok, _ = check_message(u)
        if not ok:
            return

        # =====================
        # 宗门倍率
        # =====================
        from handlers.sect import apply_sect_bonus
        (
            coin_mult,
            exp_mult,
            qi_mult,
            luck_mult
        ) = apply_sect_bonus(u)

        # =====================
        # 基础奖励
        # =====================
        reward_data = reward()
        base_coins = reward_data["coins"]
        base_xp = reward_data["xp"]
        base_qi = reward_data["qi"]

        # =====================
        # 应用宗门倍率
        # =====================
        final_coins = int(base_coins * coin_mult)
        final_xp = int(base_xp * exp_mult)
        final_qi = int(base_qi * qi_mult)

        # =====================
        # 发放经验 / 灵气
        # =====================
        u.xp += final_xp
        u.qi += final_qi

        # =====================
        # 幸运倍率缓存（给掉卡系统使用）
        # =====================
        context.user_data["sect_luck_mult"] = luck_mult

        # =====================
        # 金币结算（宗门抽成）
        # =====================
        final_amount = await apply_sect_tax(
            s,
            u,
            final_coins
        )

        # =====================
        # 玩家升级 + 通胀控制
        # =====================
        level_up(u)
        inflation_control(u)

        # =====================
        # 邀请系统
        # =====================
        invite_reward = track_chat_logic(s, u)
        if invite_reward:
            await context.bot.send_message(
                chat_id=invite_reward["inviter_id"],
                text=invite_reward["text"]
            )
            await update.message.reply_text("🎉 有人完成有效邀请！")

        # =====================
        # 随机事件
        # =====================
        if random.random() < 0.20:
            if random.random() < 0.15:
                event_name, value = random_event()
                message = apply_event(u, event_name, value)
                await update.message.reply_text(message)

         =====================
        ⭐ 掉卡系统（30%概率）
        # =====================
         if random.random() < 0.05:
             card = try_drop(s, u)
             if card:
                await update.message.reply_text(
                     f"🎉 掉落卡牌：{card.name} ⭐{card.rarity}"
                 )
