from telegram import Update
from telegram.ext import ContextTypes
import logging

from database import Session
from models import User, Card, get_realm_name
from services.gm_service import is_admin


async def gm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if not is_admin(uid):
        await update.message.reply_text("❌ 无权限")
        return

    if not context.args:
        await update.message.reply_text(
            "📋 GM命令用法：\n"
            "/gm addcoin <用户ID> <金币>\n"
            "/gm remcoin <用户ID> <金币>\n"
            "/gm addluck <用户ID> <数值>\n"
            "/gm remluck <用户ID> <数值>\n"
            "/gm addqi <用户ID> <数值>\n"
            "/gm remqi <用户ID> <数值>\n"
            "/gm freeze <用户ID>\n"
            "/gm unfreeze <用户ID>\n"
            "/gm setlevel <用户ID> <等级>\n"
            "/gm huishou <用户ID> <卡牌ID> <数量>   ← 回收到自己卡库\n"
            "/gm ruku <玩家ID> <卡牌ID> <数量>     ← 回收到公共库存\n"
            "/gm stock                              ← 查看牌库总库存"
        )
        return

    s = Session()

    try:
        cmd = context.args[0].lower()

        def get_user(target_id: int):
            user = s.get(User, target_id)
            if not user:
                user = User(user_id=target_id, username=f"user_{target_id}")
                s.add(user)
            return user

        # =========================
        # 金币增加
        # =========================
        if cmd == "addcoin":
            target = int(context.args[1])
            value = int(context.args[2])
            u = get_user(target)
            u.coins += value

        # =========================
        # 金币减少
        # =========================
        elif cmd == "remcoin":
            target = int(context.args[1])
            value = int(context.args[2])
            u = get_user(target)
            u.coins = max(0, u.coins - value)

        # =========================
        # 幸运增加
        # =========================
        elif cmd == "addluck":
            target = int(context.args[1])
            value = float(context.args[2])
            u = get_user(target)
            u.luck += value

        # =========================
        # 幸运减少
        # =========================
        elif cmd == "remluck":
            target = int(context.args[1])
            value = float(context.args[2])
            u = get_user(target)
            u.luck = max(0.01, u.luck - value)

        # =========================
        # 灵气增加
        # =========================
        elif cmd == "addqi":
            target = int(context.args[1])
            value = int(context.args[2])
            u = get_user(target)
            u.qi += value

        # =========================
        # 灵气减少
        # =========================
        elif cmd == "remqi":
            target = int(context.args[1])
            value = int(context.args[2])
            u = get_user(target)
            u.qi = max(0, u.qi - value)

        # =========================
        # 冻结
        # =========================
        elif cmd == "freeze":
            target = int(context.args[1])
            u = get_user(target)
            u.frozen = 1

        # =========================
        # 解冻
        # =========================
        elif cmd == "unfreeze":
            target = int(context.args[1])
            u = get_user(target)
            u.frozen = 0

        # =========================
        # 设置等级
        # =========================
        elif cmd == "setlevel":
            target = int(context.args[1])
            value = int(context.args[2])
            u = get_user(target)

            old = get_realm_name(u.level)
            u.level = value
            new = get_realm_name(u.level)

            await update.message.reply_text(
                f"✅ 用户 {target}\n"
                f"境界：{old} → {new}"
            )

        # =========================
        # 回收（玩家 → GM）
        # =========================
        elif cmd == "huishou":
            target_id = int(context.args[1])
            card_id = int(context.args[2])
            amount = int(context.args[3]) if len(context.args) > 3 else 1

            target_user = get_user(target_id)
            admin_user = get_user(uid)

            target_cards = target_user.cards or {}
            cid_str = str(card_id)

            if cid_str not in target_cards or target_cards[cid_str] < amount:
                await update.message.reply_text("❌ 目标玩家卡牌数量不足")
                return

            target_cards[cid_str] -= amount
            if target_cards[cid_str] <= 0:
                del target_cards[cid_str]
            target_user.cards = target_cards

            admin_cards = admin_user.cards or {}
            admin_cards[cid_str] = admin_cards.get(cid_str, 0) + amount
            admin_user.cards = admin_cards

            await update.message.reply_text(
                f"✅ 回收成功！\n"
                f"从用户 {target_id} 回收卡牌ID {card_id} ×{amount}\n"
                f"已加入你的卡库"
            )

        # =========================
        # 入库（玩家 → 公共库存）
        # =========================
        elif cmd == "ruku":
            if len(context.args) < 4:
                await update.message.reply_text(
                    "用法：/gm ruku <玩家ID> <卡牌ID> <数量>\n"
                    "示例：/gm ruku 123456789 1 5"
                )
                return

            target_id = int(context.args[1])
            card_id = int(context.args[2])
            amount = int(context.args[3])

            target_user = s.get(User, target_id)
            if not target_user:
                await update.message.reply_text(f"❌ 未找到玩家 {target_id}")
                return

            card = s.get(Card, card_id)
            if not card:
                await update.message.reply_text(f"❌ 未找到卡牌ID {card_id}")
                return

            target_cards = target_user.cards or {}
            cid_str = str(card_id)

            if cid_str not in target_cards or target_cards[cid_str] < amount:
                await update.message.reply_text(
                    f"❌ 玩家 {target_id} 持有 {card.name} 数量不足\n"
                    f"当前持有: {target_cards.get(cid_str, 0)}"
                )
                return

            target_cards[cid_str] -= amount
            if target_cards[cid_str] <= 0:
                del target_cards[cid_str]
            target_user.cards = target_cards

            card.remain = (card.remain or 0) + amount

            await update.message.reply_text(
                f"✅ 入库成功！\n"
                f"玩家ID: {target_id}\n"
                f"卡牌: {card.name} (ID: {card_id})\n"
                f"回收数量: {amount}\n"
                f"当前公共库存: {card.remain}"
            )

        # =========================
        # 发卡 + 群播报
        # =========================
        elif cmd == "givecard":
            if len(context.args) < 3:
                await update.message.reply_text(
                    "用法：/gm givecard <用户ID> <卡牌ID> <数量>"
                )
                return

            target_id = int(context.args[1])
            card_id = int(context.args[2])
            amount = int(context.args[3]) if len(context.args) > 3 else 1

            GROUP_ID = -1003807963429

            target_user = s.get(User, target_id)
            if not target_user:
                target_user = User(user_id=target_id, username=f"user_{target_id}")
                s.add(target_user)

            card = s.get(Card, card_id)

            if not card:
                await update.message.reply_text("❌ 卡牌ID不存在")
                return

            target_user.cards = target_user.cards or {}
            cid = str(card_id)
            target_user.cards[cid] = target_user.cards.get(cid, 0) + amount

            username = getattr(target_user, "username", None) or str(target_id)

            try:
                await context.bot.send_message(
                    chat_id=GROUP_ID,
                    text=(
                        f"🎉 <b>天降喜讯！</b>\n\n"
                        f"💎 恭喜 @{username} 运气爆棚获得空投🎉\n\n"
                        f"🃏 {card.name} ×{amount} ⭐{card.rarity}\n\n"
                        f"✨ 祝 @{username} 欧气爆棚！\n"
                        f"继续聊天还能获得更多掉落哦～"
                    ),
                    parse_mode="HTML"
                )
            except Exception as e:
                print("播报失败:", e)

            await update.message.reply_text(
                f"✅ 已成功赠送 {card.name} ×{amount} 给用户 {target_id}"
            )

        # =========================
        # 牌库库存
        # =========================
        elif cmd == "stock":
            cards = s.query(Card).all()
            if not cards:
                await update.message.reply_text("❌ 牌库暂无卡牌")
                return

            total_supply = 0
            total_remain = 0
            total_dropped = 0

            text = "📦 当前牌库总库存\n\n"

            for card in cards:
                remain = card.remain or 0
                supply = card.supply or 0
                dropped = supply - remain

                total_supply += supply
                total_remain += remain
                total_dropped += dropped

                text += (
                    f"🃏 {card.name} (ID: {card.id})\n"
                    f"   ⭐ {card.rarity}   库存: {remain}/{supply}\n"
                    f"   已掉落: {dropped}\n\n"
                )

            text += (
                f"📊 总计\n"
                f"全部卡牌总供应: {total_supply}\n"
                f"当前剩余库存: {total_remain}\n"
                f"已掉落总量: {total_dropped}\n"
            )

            await update.message.reply_text(text)
            return

        else:
            await update.message.reply_text("❌ 未知命令")
            return

        s.commit()

        if cmd not in ["huishou", "setlevel", "ruku", "stock"]:
            await update.message.reply_text(
                f"✅ GM执行成功\n目标用户: {target if 'target' in locals() else '未知'}"
            )

    except (ValueError, IndexError):
        await update.message.reply_text("❌ 参数错误！")
    except Exception as e:
        logging.error(f"GM错误: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 执行失败: {str(e)}")
    finally:
        s.close()
