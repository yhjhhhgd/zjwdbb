from telegram import Update
from telegram.ext import ContextTypes
from database import get_session
from models import User
from config import ADMIN_IDS


async def bind_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    if user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ 你没有权限执行此操作")
        return

    if len(args) != 2:
        await update.message.reply_text(
            "📌 使用方法：\n/bind <新人ID> <邀请人ID>\n\n示例：/bind 8746929805 7868360064"
        )
        return

    try:
        new_user_id = int(args[0])
        inviter_id = int(args[1])

        with get_session() as s:
            target_user = s.get(User, new_user_id)
            if not target_user:
                target_user = User(user_id=new_user_id, username=f"user_{new_user_id}")
                s.add(target_user)

            old = target_user.inviter_id
            target_user.inviter_id = inviter_id
            s.commit()

        await update.message.reply_text(f"✅ 绑定成功！\n新人: {new_user_id} → 邀请人: {inviter_id}\n原绑定: {old or '无'}")
    except Exception as e:
        await update.message.reply_text(f"❌ 绑定失败: {e}")


async def unbind_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    if user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ 你没有权限")
        return

    if not args:
        await update.message.reply_text("/unbind <新人ID>")
        return

    try:
        uid = int(args[0])
        with get_session() as s:
            u = s.get(User, uid)
            if u:
                u.inviter_id = None
                s.commit()
                await update.message.reply_text(f"✅ 已解除用户 {uid} 的绑定")
            else:
                await update.message.reply_text("❌ 用户不存在")
    except Exception as e:
        await update.message.reply_text(f"❌ 操作失败: {e}")
