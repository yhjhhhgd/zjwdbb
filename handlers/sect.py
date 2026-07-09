import time
from telegram import Update
from telegram.ext import ContextTypes
from database import get_session
from models import User, Sect

# ===================== 辅助 =====================
def get_user_sect(session, user_id):
    user = session.get(User, user_id)
    if user and user.sect_id:
        sect = session.get(Sect, user.sect_id)
        return user, sect
    return user, None

def apply_sect_bonus(user):
    """聊天加成"""
    if user.sect_id:
        return 1.5, 5.0, 5.0, 3.0
    return 1.0, 1.0, 1.0, 1.0

async def apply_sect_tax(session, user, base_coins: int):
    """宗主10%抽成 + 贡献度统计"""
    if not user.sect_id or getattr(user, 'sect_role', None) == "founder":
        return base_coins
    
    sect = session.get(Sect, user.sect_id)
    if not sect:
        return base_coins
    
    # 安全处理 None 值
    if user.contribution is None:
        user.contribution = 0
    if user.coins is None:
        user.coins = 0
    
    # 贡献度
    user.contribution += base_coins
    
    # 宗主抽成
    founder = session.get(User, sect.founder_id)
    if founder and founder.user_id != user.user_id:
        if founder.coins is None:
            founder.coins = 0
        tax = int(base_coins * 0.10)
        founder.coins += tax
        return base_coins - tax   # 弟子实际获得90%
    
    return base_coins

# ===================== 命令 =====================
async def create_sect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with get_session() as s:
        user = s.get(User, user_id)
        if user.coins < 500000:
            await update.message.reply_text("❌ 金币不足！创建宗门需要 500000 金币。")
            return
    
    context.user_data['sect_creating'] = True
    context.user_data['sect_founder'] = user_id
    await update.message.reply_text("🏛️ 请回复你的宗门名称（2-20字）：")

async def handle_sect_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """宗门创建对话"""
    if not context.user_data.get('sect_creating'):
        return False
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    if 'sect_name' not in context.user_data:
        if len(text) < 2 or len(text) > 20:
            await update.message.reply_text("❌ 名称长度 2-20 字符，请重新输入。")
            return True
        context.user_data['sect_name'] = text
        await update.message.reply_text(f"确定命名为 **{text}** 吗？\n回复【确定】创建 / 【取消】重来")
        return True
    else:
        if text in ["确定", "确认", "yes", "ok"]:
            name = context.user_data['sect_name']
            with get_session() as s:
                if s.query(Sect).filter_by(name=name).first():
                    await update.message.reply_text("❌ 名称已存在！")
                    return True
                user = s.get(User, user_id)
                user.coins -= 500000
                sect = Sect(name=name, founder_id=user_id)
                s.add(sect)
                s.commit()
                user.sect_id = sect.id
                user.sect_role = "founder"
                s.commit()
            await update.message.reply_text(f"🎉 **{name}** 宗门创建成功！你已成为宗主！")
            context.user_data.clear()
            return True
        elif text in ["取消", "cancel"]:
            context.user_data.pop('sect_name', None)
            await update.message.reply_text("🔄 请重新输入宗门名称：")
            return True
    return False

async def sect_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with get_session() as s:
        user, sect = get_user_sect(s, user_id)
        if not sect:
            await update.message.reply_text("❌ 你未加入宗门。/create_sect 创建")
            return
        
        members = s.query(User).filter_by(sect_id=sect.id).all()
        member_text = "\n".join([
            f"• {m.username or 'ID:'+str(m.user_id)} {'[宗主]' if m.sect_role=='founder' else '[长老]' if m.sect_role=='elder' else ''} (贡献:{m.contribution or 0})"
            for m in members
        ])
        
        text = f"""🏛️ {sect.name} 宗门

等级: {sect.level}   繁荣度: {sect.prosperity}
成员数量: {len(members)} 人

📋 成员列表:
{member_text}
"""
        await update.message.reply_text(text, parse_mode=None)  # 关键：关闭 Markdown

async def join_sect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("用法：/join <宗门名称>")
        return
    name = " ".join(args)
    with get_session() as s:
        user = s.get(User, user_id)
        if user.sect_id:
            await update.message.reply_text("❌ 你已在其他宗门！")
            return
        sect = s.query(Sect).filter_by(name=name).first()
        if not sect or user.coins < 20000:
            await update.message.reply_text("❌ 宗门不存在或金币不足（需20000）！")
            return
        user.coins -= 20000
        founder = s.get(User, sect.founder_id)
        if founder:
            founder.coins += int(20000 * 0.8)
        user.sect_id = sect.id
        sect.member_count += 1
        s.commit()
        await update.message.reply_text(f"🎊 成功加入 **{sect.name}**！")

async def sect_kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """踢出宗门 /kick <目标用户ID或@用户名>"""
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("用法：/kick <用户ID>")
        return
    try:
        target_id = int(args[0])
    except:
        await update.message.reply_text("请输入有效用户ID")
        return
    with get_session() as s:
        user, sect = get_user_sect(s, user_id)
        if not sect or user.sect_role not in ["founder", "elder"]:
            await update.message.reply_text("❌ 只有宗主或长老可踢人！")
            return
        target = s.get(User, target_id)
        if not target or target.sect_id != sect.id:
            await update.message.reply_text("❌ 该用户不在本宗门！")
            return
        if target.sect_role == "founder":
            await update.message.reply_text("❌ 无法踢出宗主！")
            return
        target.sect_id = None
        target.sect_role = None
        sect.member_count -= 1
        s.commit()
        await update.message.reply_text(f"✅ 已将用户 {target_id} 踢出宗门")

async def sect_elder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """任命长老 /elder <用户ID>"""
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("用法：/elder <用户ID>")
        return
    try:
        target_id = int(args[0])
    except:
        await update.message.reply_text("请输入有效用户ID")
        return
    with get_session() as s:
        user, sect = get_user_sect(s, user_id)
        if not sect or user.sect_role != "founder":
            await update.message.reply_text("❌ 只有宗主可任命长老！")
            return
        target = s.get(User, target_id)
        if not target or target.sect_id != sect.id:
            await update.message.reply_text("❌ 用户不在本宗门！")
            return
        target.sect_role = "elder"
        s.commit()
        await update.message.reply_text(f"✅ 已任命用户 {target_id} 为长老")

# ===================== 导出 =====================
__all__ = ['create_sect', 'handle_sect_message', 'sect_info', 'join_sect', 'sect_kick', 'sect_elder', 'apply_sect_bonus', 'apply_sect_tax']
