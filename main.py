import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ChatJoinRequestHandler
)

from config import BOT_TOKEN
from database import init_db

from handlers.user import start, my, cards, chat
from handlers.gm import gm
from handlers.market import market, buy, sell, market_callback
from telegram.ext import CallbackQueryHandler

from handlers.pk import pk
from handlers.invite import generate_invite_link, handle_join_request, my_invite
from handlers.market_hq import hq
from handlers.admin import bind_invite, unbind_invite
logging.basicConfig(level=logging.INFO)

def main():

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    # 用户命令

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("my", my))

    app.add_handler(CommandHandler("cards", cards))

    app.add_handler(CommandHandler("pk", pk))

    app.add_handler(CommandHandler("invite", generate_invite_link))

    app.add_handler(CommandHandler("myinvite", my_invite))
    application.add_handler(CommandHandler("bind", bind_invite))
    application.add_handler(CommandHandler("unbind", unbind_invite))

    # 市场

    app.add_handler(CommandHandler("sell", sell))

    app.add_handler(CommandHandler("market", market))
    app.add_handler(CallbackQueryHandler(market_callback, pattern="^market_"))

    app.add_handler(CommandHandler("buy", buy))

    #app.add_handler(CommandHandler("orders", my_orders))
    app.add_handler(CommandHandler("hq", hq))
    # =====================

# 邀请系统

# =====================

    app.add_handler(

    CommandHandler(

        "invite",

        generate_invite_link

    )

)

    app.add_handler(

    CommandHandler(

        "myinvite",

        my_invite

    )

)

# 新人申请加入监听

    app.add_handler(

    ChatJoinRequestHandler(

        handle_join_request

    )

)

# 

    # GM

    app.add_handler(CommandHandler("gm", gm))

   
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
