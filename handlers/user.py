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
    try:
        with get_session() as s:
            u = get_user(s, update.effective_user.id, update.effective_user.username)

            print(f"【DEBUG】用户 {u.user_id}({getattr(u, 'username', 'N/A')}) 进入聊天")

            # ===================== 反作弊 =====================
            ok, last_time = check_message(u)
            print(f"【DEBUG】反作弊: {ok} | last_msg={getattr(u, 'last_msg', 0)}")
            if not ok:
                print("【DEBUG】被反作弊拦截")
                return

            # ===================== 基础收益 =====================
            print(f"【DEBUG】修改前 -> coins={u.coins}, xp={u.xp}, qi={u.qi}, level={u.level}")
            
            reward(u)
            level_up(u)
            inflation_control(u)
            
            print(f"【DEBUG】修改后 -> coins={u.coins}, xp={u.xp}, qi={u.qi}, level={u.level}")

            s.refresh(u)   # 确保对象更新

            # ===================== 掉卡+事件（临时提高概率测试） =====================
            if random.random() < 0.30:

                if random.random() < 0.25:
                    event_name, value = random_event()
                    message = apply_event(u, event_name, value)
                    await update.message.reply_text(message)

                card = try_drop(s, u)
                if card:
                    await update.message.reply_text(
                        f"🎉 掉落卡牌：{card.name} ⭐{card.rarity}"
                    )

            s.commit()
            print("【DEBUG】聊天处理完成并 commit")

    except Exception as e:
        print(f"【ERROR】聊天函数异常: {e}", exc_info=True)
        try:
            await update.message.reply_text(f"调试错误: {str(e)[:200]}")
        except:
            pass
