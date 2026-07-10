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
from handlers.pk import pk
from handlers.invite import generate_invite_link, handle_join_request, my_invite
from handlers.market_hq import hq
from handlers.admin import bind_invite, unbind_invite
from handlers.sect import create_sect, sect_info, join_sect, handle_sect_message, sect_kick, sect_elder
from handlers.spirit_shop import register_spirit_handlers
logging.basicConfig(level=logging.INFO)


def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    # ===================== 用户命令 =====================
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("my", my))
    app.add_handler(CommandHandler("cards", cards))
    app.add_handler(CommandHandler("pk", pk))
    app.add_handler(CommandHandler("invite", generate_invite_link))
    app.add_handler(CommandHandler("myinvite", my_invite))
    app.add_handler(CommandHandler("create_sect", create_sect))
    app.add_handler(CommandHandler("kszm", create_sect))
    app.add_handler(CommandHandler("sect", sect_info))
    app.add_handler(CommandHandler("join", join_sect))
    app.add_handler(CommandHandler("kick", sect_kick))
    app.add_handler(CommandHandler("elder", sect_elder))

    # ===================== 市场相关 =====================
    app.add_handler(CommandHandler("sell", sell))
    app.add_handler(CommandHandler("market", market))
    app.add_handler(CallbackQueryHandler(market_callback, pattern="^market_"))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("hq", hq))

    # ===================== 管理员命令 =====================
    app.add_handler(CommandHandler("bind", bind_invite))
    app.add_handler(CommandHandler("unbind", unbind_invite))

    # ===================== GM 命令 =====================
    app.add_handler(CommandHandler("gm", gm))

    # ===================== 邀请系统 =====================
    app.add_handler(ChatJoinRequestHandler(handle_join_request))

    # ===================== 群聊消息处理（仅指定群生效） =====================
    ALLOWED_GROUP_ID = -1003807963429  # ← 你的群ID

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND &
            (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP) &
            filters.Chat(chat_id=ALLOWED_GROUP_ID),
            chat
        )
    )
    register_spirit_handlers(app)

    print("🚀 V4 重构版系统启动成功 - 仅指定群聊掉落生效")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
