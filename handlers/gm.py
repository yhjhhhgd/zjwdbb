from telegram import Update
from telegram.ext import ContextTypes

from database import Session
from models import User
from services.gm_service import is_admin


async def gm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if not is_admin(uid):
        await update.message.reply_text("❌ 无权限")
        return

    s = Session()
    cmd = context.args[0]

    if cmd == "addcoin":
        target = int(context.args[1])
        value = int(context.args[2])
        u = s.get(User, target)
        u.coins += value

    elif cmd == "freeze":
        target = int(context.args[1])
        u = s.get(User, target)
        u.frozen = 1

    elif cmd == "unfreeze":
        target = int(context.args[1])
        u = s.get(User, target)
        u.frozen = 0

    elif cmd == "setlevel":
        target = int(context.args[1])
        value = int(context.args[2])
        u = s.get(User, target)
        u.level = value

    s.commit()
    s.close()

    await update.message.reply_text("✅ GM执行成功")
