from telegram import Update
from telegram.ext import ContextTypes
import random

from database import get_session
from models import User, Card

from core.pk import (
    get_pk_limit,
    calculate_win_rate,
    get_win_text,
    get_lose_text,
    calculate_pk_cost,
    check_pk_cost
)


async def pk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("请回复对方的消息，并输入 /pk 你的卡牌ID")
        return

    try:
        my_card_id = int(context.args[0])
    except:
        await update.message.reply_text("用法：回复对方消息 + /pk 你的卡牌ID")
        return

    opponent_id = update.message.reply_to_message.from_user.id
    my_id = update.effective_user.id

    if opponent_id == my_id:
        await update.message.reply_text("不能和自己PK！")
        return

    with get_session() as s:
        me = s.get(User, my_id)
        opponent = s.get(User, opponent_id)

        if not me or not opponent:
            await update.message.reply_text("玩家数据异常")
            return

        # ======================
        # PK次数限制
        # ======================
        can_pk, msg = get_pk_limit(me)
        if not can_pk:
            await update.message.reply_text(msg)
            return

        # ======================
        # 我的卡牌
        # ======================
        my_cards = me.cards or {}

        if str(my_card_id) not in my_cards or my_cards[str(my_card_id)] < 1:
            await update.message.reply_text("你没有这张卡牌")
            return

        my_card = s.get(Card, my_card_id)
        if not my_card:
            await update.message.reply_text("卡牌不存在")
            return

        # ======================
        # PK消耗（重点修改）
        # ======================
        qi_cost, coin_cost = calculate_pk_cost(me, my_card)

        ok, msg = check_pk_cost(me, qi_cost, coin_cost)
        if not ok:
            await update.message.reply_text(msg)
            return

        me.qi -= qi_cost
        me.coins -= coin_cost
        me.pk_count_today += 1

        # ======================
        # 对方卡牌
        # ======================
        opp_cards = opponent.cards or {}
        if not opp_cards:
            await update.message.reply_text("对方没有卡牌，无法PK")
            return

        opp_card_id = random.choice(list(opp_cards.keys()))
        opp_card = s.get(Card, int(opp_card_id))

        if not opp_card:
            await update.message.reply_text("对方卡牌异常")
            return

        # ======================
        # PK计算
        # ======================
        win_rate = calculate_win_rate(my_card.power, opp_card.power)
        is_win = random.randint(1, 100) <= win_rate

        # ======================
        # 胜利
        # ======================
        if is_win:
            cid = str(opp_card.id)

            opp_cards[cid] -= 1
            if opp_cards[cid] <= 0:
                del opp_cards[cid]
            opponent.cards = opp_cards

            my_cards[cid] = my_cards.get(cid, 0) + 1
            me.cards = my_cards

            text = get_win_text(my_card, opp_card)
            await update.message.reply_text(
                f"🎉 {text}\n你获得了对方的 {opp_card.name}！"
            )

        # ======================
        # 失败（不变）
        # ======================
        else:
            cid = str(my_card.id)

            if cid in my_cards:
                my_cards[cid] -= 1
                if my_cards[cid] <= 0:
                    del my_cards[cid]

            me.cards = my_cards

            opp_cards = opponent.cards or {}
            opp_cards[cid] = opp_cards.get(cid, 0) + 1
            opponent.cards = opp_cards

            text = get_lose_text(my_card, opp_card)
            await update.message.reply_text(
                f"😔 {text}\n你失去了 {my_card.name}，已被对方夺走！"
            )
