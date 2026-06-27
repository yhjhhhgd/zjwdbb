import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN
from database import init_db

from handlers.user import start, my, chat
from handlers.gm import gm
from handlers.market import sell, market, buy, my_orders

logging.basicConfig(level=logging.INFO)


def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("my", my))
    app.add_handler(CommandHandler("gm", gm))

    app.add_handler(CommandHandler("sell", sell))
    app.add_handler(CommandHandler("market", market))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("orders", my_orders))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🚀 V4 FULL SYSTEM READY")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
