from telegram import Update
from telegram.ext import ContextTypes

from database import get_session
from models import User
from services.gm_service import is_admin

async def gm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("❌ 无管理员权限")
        return

    if not context.args:
        await update.message.reply_text(
            "用法示例：\n"
            "/gm addcoin 用户ID 金额\n"
            "/gm freeze 用户ID\n"
            "/gm unfreeze 用户ID\n"
            "/gm setlevel 用户ID 等级"
        )
        return

    try:
        cmd = context.args[0].lower()
        with get_session() as s:
            if cmd == "addcoin":
                target = int(context.args[1])
                value = int(context.args[2])
                u = s.get(User, target)
                if u:
                    u.coins += value
                    await update.message.reply_text(f"✅ 已为 {target} 添加 {value} 金币")
                else:
                    await update.message.reply_text("❌ 用户不存在")

            elif cmd == "freeze":
                target = int(context.args[1])
                u = s.get(User, target)
                if u:
                    u.frozen = 1
                    await update.message.reply_text(f"✅ 已冻结用户 {target}")

            elif cmd == "unfreeze":
                target = int(context.args[1])
                u = s.get(User, target)
                if u:
                    u.frozen = 0
                    await update.message.reply_text(f"✅ 已解冻用户 {target}")

            elif cmd == "setlevel":
                target = int(context.args[1])
                value = int(context.args[2])
                u = s.get(User, target)
                if u:
                    u.level = value
                    await update.message.reply_text(f"✅ 已设置用户 {target} 等级为 {value}")

            else:
                await update.message.reply_text("❌ 未知GM命令")

    except (IndexError, ValueError):
        await update.message.reply_text("❌ 参数错误，请检查命令格式")
    except Exception as e:
        await update.message.reply_text(f"❌ 执行失败: {str(e)}")
