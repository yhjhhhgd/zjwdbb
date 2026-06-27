import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN
from database import init_db

# user.py
from handlers.user import start, my, chat, cards

# gm.py
from handlers.gm import gm

# market.py
from handlers.market import sell, market, buy, my_orders

logging.basicConfig(level=logging.INFO)


def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    # 用户命令
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("my", my))
    app.add_handler(CommandHandler("cards", cards))

    # 市场命令
    app.add_handler(CommandHandler("sell", sell))
    app.add_handler(CommandHandler("market", market))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("orders", my_orders))

    # GM命令
    app.add_handler(CommandHandler("gm", gm))

    # 聊天监听
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    print("🚀 V4 FULL SYSTEM READY")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
