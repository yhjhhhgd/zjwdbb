import random
from telegram import Update
from telegram.ext import ContextTypes
from database import get_session
from models import User, InviteLink
from core.drop import get_available_cards


# =========================
# 生成邀请链接
# =========================
async def generate_invite_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ 请在群内使用")
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    with get_session() as s:
        old = s.query(InviteLink).filter_by(creator_id=user_id).first()
        if old:
            await update.message.reply_text(
                "🎟️ 你的专属邀请链接:\n\n"
                f"{old.link}\n\n"
                "新人通过此链接申请加入即可绑定"
            )
            return

    try:
        link = await context.bot.create_chat_invite_link(
            chat_id=chat_id,
            creates_join_request=True,
            name=f"user_{user_id}"
        )

        with get_session() as s:
            s.add(InviteLink(link=link.invite_link, creator_id=user_id))
            s.commit()

        await update.message.reply_text(
            "🎟️ 创建成功\n\n"
            f"{link.invite_link}\n\n"
            "规则：\n新人加入后聊天180条成为有效邀请\n奖励：500金币+随机卡牌"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ 创建失败: {e}")


# =========================
# 新人申请加入（已优化）
# =========================
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    user_id = request.from_user.id
    chat_id = request.chat.id
    inviter_id = None

    try:
        with get_session() as s:
            invite = request.invite_link
            link_received = None

            if invite and invite.invite_link:
                link_received = invite.invite_link.strip()
                print(f"[INVITE] 收到链接: {link_received}")

                # 多种方式查询邀请记录
                record = None
                
                # 方式1: 精确匹配
                record = s.query(InviteLink).filter_by(link=link_received).first()

                # 方式2: 如果失败，尝试去掉参数后匹配
                if not record and '?' in link_received:
                    clean_link = link_received.split('?')[0]
                    record = s.query(InviteLink).filter_by(link=clean_link).first()

                # 方式3: 模糊匹配（包含相同哈希部分）
                if not record:
                    records = s.query(InviteLink).all()
                    for r in records:
                        if r.link and link_received in r.link or r.link in link_received:
                            record = r
                            print(f"[INVITE] 模糊匹配成功: {r.link}")
                            break

                if record:
                    inviter_id = record.creator_id
                    print(f"[INVITE SUCCESS] 新人 {user_id} 绑定邀请人 {inviter_id}")
                else:
                    print(f"[INVITE FAIL] 未找到对应邀请记录")

            # 创建/更新用户
            user = s.get(User, user_id)
            if not user:
                user = User(
                    user_id=user_id,
                    username=request.from_user.full_name or f"user_{user_id}"
                )
                s.add(user)

            if inviter_id:
                user.inviter_id = inviter_id
            else:
                print(f"[INVITE] 新人 {user_id} 未绑定邀请人")

            s.commit()

    except Exception as e:
        print(f"[INVITE ERROR] {e}")

    # 自动批准
    await context.bot.approve_chat_join_request(
        chat_id=chat_id, user_id=user_id
    )

# =========================
# 聊天奖励逻辑（保持不变）
# =========================
def track_chat_logic(session, user):
    if user.msg_count is None:
        user.msg_count = 0
    if user.rewarded is None:
        user.rewarded = 0

    user.msg_count += 1

    reward_data = None

    if (
        user.inviter_id
        and user.rewarded == 0
        and user.msg_count >= 180
    ):
        inviter = session.get(User, user.inviter_id)
        if inviter:
            if inviter.invited_count is None:
                inviter.invited_count = 0
            if inviter.coins is None:
                inviter.coins = 0

            inviter.invited_count += 1
            inviter.coins += 500

            text = (
                "🎉 有效邀请完成\n\n"
                f"👤 新成员: {user.username}\n"
                "💰 奖励: +500金币\n"
                f"📊 当前邀请: {inviter.invited_count}"
            )

            # 卡牌奖励
            try:
                cards = get_available_cards(session)
                if cards:
                    select = random.sample(cards, min(2, len(cards)))
                    text += "\n🎴 卡牌:"
                    if inviter.cards is None:
                        inviter.cards = {}
                    for c in select:
                        cid = str(c.id)
                        inviter.cards[cid] = inviter.cards.get(cid, 0) + 1
                        text += f"\n• {c.name}"
            except:
                pass

            user.rewarded = 1
            reward_data = {
                "inviter_id": inviter.user_id,
                "text": text
            }

    return reward_data


# =========================
# 查询邀请（已增强）
# =========================
async def my_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    with get_session() as s:
        user = s.get(User, uid)
        if not user:
            await update.message.reply_text("❌ 暂无数据")
            return

        # 有效邀请（已完成180条）
        effective_count = user.invited_count or 0

        # 总邀请人数（所有通过我链接加入的，不管是否有效）
        total_invited = s.query(User).filter_by(inviter_id=uid).count()

        await update.message.reply_text(
            "📊 邀请中心\n\n"
            f"👥 总邀请人数: {total_invited}\n"
            f"✅ 有效邀请: {effective_count}\n"
            f"💰 已获得金币: {effective_count * 500}\n\n"
            f"💡 提示：新人需发言满 180 条才算有效\n"
            "新人通过你的专属链接加入后会自动统计"
        )
