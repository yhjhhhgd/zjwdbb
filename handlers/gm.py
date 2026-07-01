from telegram import Update
from telegram.ext import ContextTypes

from database import get_session
from models import User, get_realm_name   # ← 修改这里，加上 get_realm_name
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
    if len(context.args) < 3:
        raise ValueError("参数不足")
    target = int(context.args[1])
    value = int(context.args[2])
    
    u = s.get(User, target)
    if not u:
        u = User(user_id=target, username=f"user_{target}")
        s.add(u)
    
    old_realm = get_realm_name(u.level)      # ← 新增
    u.level = value
    new_realm = get_realm_name(u.level)      # ← 新增
    
    await update.message.reply_text(
        f"✅ 已将用户 {target} 的等级设置为 {value}\n"
        f"境界：{old_realm} → {new_realm}"
    )

            else:
                await update.message.reply_text("❌ 未知GM命令")

    except (IndexError, ValueError):
        await update.message.reply_text("❌ 参数错误，请检查命令格式")
    except Exception as e:
        await update.message.reply_text(f"❌ 执行失败: {str(e)}")
