import random
from telegram import Update
from telegram.ext import ContextTypes
from database import get_session
from models import User, Card
from core.drop import get_available_cards


async def generate_invite_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """生成专属邀请链接"""
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ 请在群内使用 /invite")
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    try:
        link = await context.bot.create_chat_invite_link(
            chat_id=chat_id,
            name=f"邀请_{user_id}",
            member_limit=0,
            expire_date=None
        )

        await update.message.reply_text(
            f"🎟️ **你的专属邀请链接**\n\n"
            f"{link.invite_link}\n\n"
            f"✅ 每邀请1人成功加入：\n"
            f"💰 +500 金币\n"
            f"🎴 1~3 张随机卡牌\n"
            f"📈 被邀请人 **聊天收益的 30%** 长期归你"
        )
    except Exception:
        await update.message.reply_text("❌ 生成失败，请确认 Bot 是管理员且有邀请权限")


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """自动追踪新人 + 绑定 + 即时奖励"""
    if not update.chat_member or not update.chat_member.new_chat_member:
        return

    new_member = update.chat_member.new_chat_member.user
    if new_member.is_bot:
        return

    inviter_id = None
    if hasattr(update.chat_member, 'invite_link') and update.chat_member.invite_link:
        link_name = getattr(update.chat_member.invite_link, 'name', '')
        if link_name.startswith("邀请_"):
            try:
                inviter_id = int(link_name.split("_")[1])
            except:
                pass

    if not inviter_id:
        return

    with get_session() as s:
        # 新人信息
        new_user = s.get(User, new_member.id)
        if not new_user:
            new_user = User(user_id=new_member.id, username=new_member.username or new_member.full_name)
            s.add(new_user)
        new_user.inviter_id = inviter_id

        # 邀请者数据
        inviter = s.get(User, inviter_id)
        if inviter:
            inviter.invited_count = (inviter.invited_count or 0) + 1

            # 即时奖励
            inviter.coins = (inviter.coins or 0) + 500

            available_cards = get_available_cards(s)
            reward_text = f"🎉 邀请成功！新人：{new_member.full_name}\n💰 +500 金币\n"

            if available_cards:
                num = random.randint(1, 3)
                selected = random.sample(available_cards, min(num, len(available_cards)))
                reward_text += "🎴 获得卡牌：\n"
                for card in selected:
                    cid = str(card.id)
                    inviter.cards = inviter.cards or {}
                    inviter.cards[cid] = inviter.cards.get(cid, 0) + 1
                    if hasattr(card, 'remain') and card.remain > 0:
                        card.remain -= 1
                    reward_text += f"• {card.name} ⭐{card.rarity}\n"

            try:
                await context.bot.send_message(chat_id=inviter_id, text=reward_text)
            except:
                pass

        s.commit()


def give_master_share(session, user, coins_gained: int):
    """师徒分成：邀请人获得30%"""
    if not user.inviter_id or coins_gained <= 0:
        return 0

    master = session.get(User, user.inviter_id)
    if not master:
        return 0

    share = int(coins_gained * 0.3)
    master.coins = (master.coins or 0) + share

    return share
