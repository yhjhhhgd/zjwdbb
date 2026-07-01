from telegram import Update
from telegram.ext import ContextTypes
import logging

from database import Session
from models import User, get_realm_name
from services.gm_service import is_admin


async def gm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if not is_admin(uid):
        await update.message.reply_text("❌ 无权限")
        return

    if not context.args:
        await update.message.reply_text(
            "📋 GM命令用法：\n"
            "/gm addcoin <用户ID> <金币数量>\n"
            "/gm freeze <用户ID>\n"
            "/gm unfreeze <用户ID>\n"
            "/gm setlevel <用户ID> <等级>"
        )
        return

    s = Session()
    try:
        cmd = context.args[0].lower()

        if cmd == "addcoin":
            if len(context.args) < 3:
                raise ValueError("参数不足")
            target = int(context.args[1])
            value = int(context.args[2])
            u = s.get(User, target)
            if not u:
                u = User(user_id=target, username=f"user_{target}")
                s.add(u)
            u.coins += value

        elif cmd == "freeze":
            target = int(context.args[1])
            u = s.get(User, target)
            if not u:
                u = User(user_id=target, username=f"user_{target}")
                s.add(u)
            u.frozen = 1

        elif cmd == "unfreeze":
            target = int(context.args[1])
            u = s.get(User, target)
            if not u:
                u = User(user_id=target, username=f"user_{target}")
                s.add(u)
            u.frozen = 0

        elif cmd == "setlevel":
            if len(context.args) < 3:
                raise ValueError("参数不足")
            target = int(context.args[1])
            value = int(context.args[2])
            u = s.get(User, target)
            if not u:
                u = User(user_id=target, username=f"user_{target}")
                s.add(u)
            
            old_realm = get_realm_name(u.level)
            u.level = value
            new_realm = get_realm_name(u.level)
            
            await update.message.reply_text(
                f"✅ 已将用户 {target} 的等级设置为 {value}\n"
                f"境界：{old_realm} → {new_realm}"
            )
            s.commit()
            s.close()
            return

        else:
            await update.message.reply_text("❌ 未知命令")
            s.close()
            return

        s.commit()
        await update.message.reply_text(f"✅ GM执行成功\n目标用户: {target}")

    except (ValueError, IndexError):
        await update.message.reply_text("❌ 参数错误！请检查用法")
    except Exception as e:
        logging.error(f"GM命令错误: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 执行失败: {str(e)}")
    finally:
        s.close()
