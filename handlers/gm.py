from telegram import Update
from telegram.ext import ContextTypes
import logging

from database import Session
from models import User, get_realm_name
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
            "/gm huishou <用户ID> <卡牌ID> <数量>   ← 新增回收命令"
        )
        return

    s = Session()

    try:
        cmd = context.args[0].lower()

        target = None
        u = None

        # =========================
        # 获取用户
        # =========================
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

        # ======================== 新增：回收卡牌 ========================
        elif cmd == "huishou":
            target_id = int(context.args[1])
            card_id = int(context.args[2])
            amount = int(context.args[3]) if len(context.args) > 3 else 1

            target_user = get_user(target_id)
            admin_user = get_user(uid)   # 管理员自己

            target_cards = target_user.cards or {}
            cid_str = str(card_id)

            if cid_str not in target_cards or target_cards[cid_str] < amount:
                await update.message.reply_text("❌ 目标玩家卡牌数量不足")
                return

            # 从目标玩家扣除
            target_cards[cid_str] -= amount
            if target_cards[cid_str] <= 0:
                del target_cards[cid_str]
            target_user.cards = target_cards

            # 加入管理员卡库
            admin_cards = admin_user.cards or {}
            admin_cards[cid_str] = admin_cards.get(cid_str, 0) + amount
            admin_user.cards = admin_cards

            await update.message.reply_text(
                f"✅ 回收成功！\n"
                f"从用户 {target_id} 回收卡牌ID {card_id} ×{amount}\n"
                f"已加入你的卡库"
            )

        else:
            await update.message.reply_text("❌ 未知命令")
            return

        s.commit()

        if cmd != "huishou" and cmd != "setlevel":
            await update.message.reply_text(
                f"✅ GM执行成功\n目标用户: {target}"
            )

    except (ValueError, IndexError):
        await update.message.reply_text("❌ 参数错误！\n回收命令示例：/gm huishou 用户ID 卡牌ID 数量")
    except Exception as e:
        logging.error(f"GM错误: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 执行失败: {str(e)}")
    finally:
        s.close()
