import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN
from database import init_db

from handlers.user import start, my, cards, chat
from handlers.gm import gm
from handlers.market import sell, market, buy, my_orders
from handlers.pk import pk
logging.basicConfig(level=logging.INFO)

def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    # 用户命令
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("my", my))
    app.add_handler(CommandHandler("cards", cards))
    app.add_handler(CommandHandler("pk", pk))
    # 市场命令
    app.add_handler(CommandHandler("sell", sell))
    app.add_handler(CommandHandler("market", market))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("orders", my_orders))

    # GM命令
    app.add_handler(CommandHandler("gm", gm))

    # 只在群聊触发聊天奖励（已修正过滤器）
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & 
            (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP),
            chat
        )
    )

    print("🚀 V4 重构版系统启动成功 - 仅群聊掉落生效")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
