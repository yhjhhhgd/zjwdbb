import random
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from database import get_session
from models import User
from core.drop import get_available_cards


# =========================
# 邀请链接存储模型依赖说明
# =========================
# 你必须有 InviteLink 表（下面我会告诉你怎么加）


# =========================
# 1. 生成邀请链接
# =========================
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
            name=f"inv_{user_id}",
            member_limit=0
        )

        # 存映射关系（关键）
        from models import InviteLink

        with get_session() as s:
            s.add(InviteLink(
                link=link.invite_link,
                creator_id=user_id
            ))
            s.commit()

        await update.message.reply_text(
            f"🎟️ 你的专属邀请链接\n\n"
            f"{link.invite_link}\n\n"
            f"📌 规则：新人需聊天满 180 条才算有效\n"
            f"💰 奖励：500金币 + 随机卡牌"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ 生成失败：{e}")


# =========================
# 2. 新人进群处理
# =========================
async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """新人进群绑定邀请人"""

    message = update.message
    if not message or not message.new_chat_members:
        return

    with get_session() as s:

        from models import InviteLink

        for member in message.new_chat_members:

            if member.is_bot:
                continue

            inviter_id = None

            # Telegram 绑定 invite_link
            invite_link = message.invite_link

            if invite_link:
                record = (
                    s.query(InviteLink)
                    .filter_by(link=invite_link.invite_link)
                    .first()
                )
                if record:
                    inviter_id = record.creator_id

            # 写入用户
            user = s.get(User, member.id)
            if not user:
                user = User(
                    user_id=member.id,
                    username=member.full_name,
                    msg_count=0,
                    rewarded=False
                )
                s.add(user)

            user.inviter_id = inviter_id

            s.commit()

            # 群提示
            if inviter_id:
                try:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"👋 {member.full_name} 加入群聊\n🎯 邀请人：{inviter_id}"
                    )
                except:
                    pass


# =========================
# 3. 聊天计数 + 有效邀请判断
# =========================
async def track_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """统计聊天数 + 满180条发奖励"""

    message = update.message
    if not message or not message.from_user:
        return

    user_id = message.from_user.id

    with get_session() as s:

        user = s.get(User, user_id)
        if not user:
            return

        user.msg_count = (user.msg_count or 0) + 1

        # 满180条触发有效邀请
        if (
            user.inviter_id and
            not user.rewarded and
            user.msg_count >= 180
        ):
            inviter = s.get(User, user.inviter_id)

            reward_text = f"🎉 有效邀请达成！\n👤 {user.username}\n💰 +500金币"

            if inviter:
                inviter.invited_count = (inviter.invited_count or 0) + 1
                inviter.coins = (inviter.coins or 0) + 500

                reward_text += f"\n📊 当前有效邀请：{inviter.invited_count}"

                # 随机卡牌
                available_cards = get_available_cards(s)
                if available_cards:
                    num = random.randint(1, 3)
                    selected = random.sample(
                        available_cards,
                        min(num, len(available_cards))
                    )

                    reward_text += "\n🎴 卡牌："
                    for card in selected:
                        inviter.cards = inviter.cards or {}
                        cid = str(card.id)
                        inviter.cards[cid] = inviter.cards.get(cid, 0) + 1
                        reward_text += f"\n• {card.name}"

            user.rewarded = True
            s.commit()

            # 私聊通知邀请人
            if inviter:
                try:
                    await context.bot.send_message(
                        chat_id=inviter.user_id,
                        text=reward_text
                    )
                except:
                    pass


# =========================
# 4. 邀请数据查询
# =========================
async def my_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看邀请统计"""

    user_id = update.effective_user.id

    with get_session() as s:
        user = s.get(User, user_id)

        if not user:
            await update.message.reply_text("❌ 无数据")
            return

        total = user.invited_count or 0
        coins = total * 500

        await update.message.reply_text(
            "📊 邀请中心\n\n"
            f"👥 总邀请：{total}\n"
            f"🎯 有效邀请：{total}\n"
            f"💰 已获得：{coins} 金币\n"
            f"📌 每个有效邀请需 180 条聊天"
        )
