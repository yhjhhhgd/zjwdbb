from telegram import Update
from telegram.ext import ContextTypes
from database import get_session
from services.market_service import get_zodiac_overview, get_zodiac_detail


async def hq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_session() as s:
        args = context.args

        if args:  # /hq 鼠
            zodiac = args[0].strip()
            text = get_zodiac_detail(s, zodiac)
        else:     # /hq
            text = get_zodiac_overview(s)

        await update.message.reply_text(text, parse_mode="Markdown")
