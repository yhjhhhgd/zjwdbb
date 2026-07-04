from telegram import Update
from telegram.ext import ContextTypes
import random   # ← 添加这一行

from database import get_session
from models import User, Card
from core.pk import get_pk_limit, calculate_win_rate, get_win_text, get_lose_text


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

        # 检查次数
        can_pk, msg = get_pk_limit(me)
        if not can_pk:
            await update.message.reply_text(msg)
            return

        # 消耗
        if me.qi < 30 or me.coins < 50:
            await update.message.reply_text("灵气或金币不足（需30灵气 + 50金币）")
            return

        me.qi -= 30
        me.coins -= 50
        me.pk_count_today += 1

        # 我的卡牌
        my_cards = me.cards or {}
        if str(my_card_id) not in my_cards or my_cards[str(my_card_id)] < 1:
            await update.message.reply_text("你没有这张卡牌")
            return

        my_card = s.get(Card, my_card_id)
        if not my_card:
            await update.message.reply_text("卡牌不存在")
            return

        # 对方随机一张卡
        opp_cards = opponent.cards or {}
        if not opp_cards:
            await update.message.reply_text("对方没有卡牌，无法PK")
            return

        opp_card_id = random.choice(list(opp_cards.keys()))
        opp_card = s.get(Card, int(opp_card_id))

        # 执行PK
        win_rate = calculate_win_rate(my_card.power, opp_card.power)
        is_win = random.randint(1, 100) <= win_rate

        if is_win:
            # 胜利：获得对方卡牌
            cid = str(opp_card.id)
            opp_cards[cid] -= 1
            if opp_cards[cid] <= 0:
                del opp_cards[cid]
            opponent.cards = opp_cards

            my_cards[cid] = my_cards.get(cid, 0) + 1
            me.cards = my_cards

            text = get_win_text(my_card, opp_card)
            await update.message.reply_text(f"🎉 {text}\n你获得了对方的 {opp_card.name}！")
        else:
            # 失败：自己出战卡牌被对方获得
            cid = str(my_card.id)

            #       自己扣卡
            if cid in my_cards:
            my_cards[cid] -= 1
            if my_cards[cid] <= 0:
                del my_cards[cid]
            me.cards = my_cards

            #       对方加卡
            opp_cards = opponent.cards or {}
            opp_cards[cid] = opp_cards.get(cid, 0) + 1
            opponent.cards = opp_cards

    text = get_lose_text(my_card, opp_card)
    await update.message.reply_text(
        f"😔 {text}\n你失去了 {my_card.name}，已被对方夺走！"
    )
    # 提交
    # with get_session 会自动 commit
