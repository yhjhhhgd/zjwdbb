from telegram import Update
from telegram.ext import ContextTypes
from database import get_session
from services.market_service import get_zodiac_overview


async def hq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_session() as s:
        args = context.args

        if args:  # /hq 鼠
            await update.message.reply_text("暂不支持单个生肖详细查询，请使用 /market 查看完整列表")
        else:     # /hq
            text = get_zodiac_overview(s)
            await update.message.reply_text(text, parse_mode="Markdown")
