from sqlalchemy import Column, Integer, String, Float, JSON, BigInteger
from sqlalchemy.ext.mutable import MutableDict
from database import Base


# =========================
# 用户表
# =========================
class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)  # Telegram ID 必须 BigInteger
    username = Column(String)
    msg_count = Column(Integer, default=0)

    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)

    coins = Column(Integer, default=100)
    qi = Column(Integer, default=0)
    luck = Column(Float, default=1.0)

    last_msg = Column(BigInteger, default=0)
    last_drop = Column(BigInteger, default=0)

    cards = Column(
        MutableDict.as_mutable(JSON),
        default=dict
    )

    frozen = Column(Integer, default=0)

    # PK系统
    pk_count_today = Column(Integer, default=0)
    last_pk_date = Column(BigInteger, default=0)

    # 邀请系统
    inviter_id = Column(BigInteger, default=None)
    invited_count = Column(Integer, default=0)


# =========================
# 卡牌表
# =========================
class Card(Base):

    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)

    name = Column(String, unique=True)     # 卡牌名

    zodiac = Column(String, index=True)    # 鼠/牛/虎...

    rarity = Column(String)               # N/R/SR/SSR/NR

    supply = Column(Integer)

    remain = Column(Integer)

    power = Column(Integer, default=100)

    price = Column(BigInteger, default=1000)

    last_price = Column(BigInteger, default=1000)

    min_price = Column(BigInteger)

    max_price = Column(BigInteger)

    change = Column(Float, default=0.0)

    


# =========================
# 市场表
# =========================
class Market(Base):
    __tablename__ = "market"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    seller_id = Column(BigInteger, nullable=False)
    card_id = Column(BigInteger, nullable=False)

    price = Column(Integer)
    amount = Column(Integer)

    created_at = Column(BigInteger, default=0)


# =========================
# 邀请链接表
# =========================
class InviteLink(Base):
    __tablename__ = "invite_links"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    link = Column(String, unique=True, nullable=False)

    creator_id = Column(BigInteger, nullable=False)


# ====================== 内置牌库 ======================
ZODIAC_CARDS = [
    # ======================
    # 原始卡牌
    # ======================

    {"name": "机敏灵鼠", "rarity": "N", "supply": 5, "remain": 5, "power": 85},
    {"name": "仓廪实鼠", "rarity": "N", "supply": 5, "remain": 5, "power": 90},
    {"name": "子夜神鼠", "rarity": "N", "supply": 5, "remain": 5, "power": 95},

    {"name": "勤耕老牛", "rarity": "N", "supply": 3, "remain": 3, "power": 100},
    {"name": "力拔山牛", "rarity": "N", "supply": 3, "remain": 3, "power": 105},
    {"name": "丑时金牛", "rarity": "N", "supply": 3, "remain": 3, "power": 110},

    {"name": "威猛猛虎", "rarity": "N", "supply": 2, "remain": 2, "power": 115},
    {"name": "山林霸虎", "rarity": "N", "supply": 2, "remain": 2, "power": 118},
    {"name": "寅虎啸月", "rarity": "N", "supply": 2, "remain": 2, "power": 122},

    {"name": "娇小玉兔", "rarity": "N", "supply": 2, "remain": 2, "power": 105},
    {"name": "月宫灵兔", "rarity": "N", "supply": 2, "remain": 2, "power": 108},
    {"name": "卯兔衔芝", "rarity": "N", "supply": 2, "remain": 2, "power": 112},

    {"name": "腾云驾蛇", "rarity": "R", "supply": 1, "remain": 1, "power": 135},
    {"name": "玄冥灵蛇", "rarity": "R", "supply": 1, "remain": 1, "power": 140},
    {"name": "巳蛇吐珠", "rarity": "R", "supply": 1, "remain": 1, "power": 145},

    {"name": "骏逸天马", "rarity": "R", "supply": 1, "remain": 1, "power": 150},
    {"name": "逐日无影马", "rarity": "R", "supply": 1, "remain": 1, "power": 155},
    {"name": "午马扬蹄", "rarity": "R", "supply": 1, "remain": 1, "power": 160},

    {"name": "温顺祥羊", "rarity": "R", "supply": 1, "remain": 1, "power": 130},
    {"name": "瑞气羊驼", "rarity": "R", "supply": 1, "remain": 1, "power": 132},
    {"name": "未羊献瑞", "rarity": "R", "supply": 1, "remain": 1, "power": 135},

    {"name": "灵敏金猴", "rarity": "SR", "supply": 1, "remain": 1, "power": 190},
    {"name": "斗战圣猴", "rarity": "SR", "supply": 1, "remain": 1, "power": 210},
    {"name": "申猴戏果", "rarity": "SR", "supply": 1, "remain": 1, "power": 195},

    {"name": "报晓金鸡", "rarity": "SR", "supply": 1, "remain": 1, "power": 180},
    {"name": "凤鸣朝阳鸡", "rarity": "SR", "supply": 1, "remain": 1, "power": 185},
    {"name": "酉鸡司晨", "rarity": "SR", "supply": 1, "remain": 1, "power": 188},

    {"name": "忠诚义狗", "rarity": "SR", "supply": 1, "remain": 1, "power": 200},
    {"name": "镇宅神犬", "rarity": "SR", "supply": 1, "remain": 1, "power": 205},
    {"name": "戌狗守夜", "rarity": "SR", "supply": 1, "remain": 1, "power": 198},

    {"name": "玄武黑猪", "rarity": "SSR", "supply": 1, "remain": 1, "power": 250},
    {"name": "亥猪拱宝", "rarity": "SSR", "supply": 1, "remain": 1, "power": 260},
    {"name": "福运肥猪", "rarity": "SSR", "supply": 1, "remain": 1, "power": 255},

    {"name": "九天神龙", "rarity": "UR", "supply": 1, "remain": 1, "power": 380},
    {"name": "哪吒闹海", "rarity": "UR", "supply": 1, "remain": 1, "power": 360},
    {"name": "辰龙吟啸", "rarity": "UR", "supply": 1, "remain": 1, "power": 400},

    {"name": "五爪金龙", "rarity": "SSR", "supply": 1, "remain": 1, "power": 290},
    {"name": "烛龙烛九阴", "rarity": "SSR", "supply": 1, "remain": 1, "power": 310},
    {"name": "青龙镇东方", "rarity": "SSR", "supply": 1, "remain": 1, "power": 295},
    {"name": "赤焰火龙", "rarity": "SSR", "supply": 1, "remain": 1, "power": 305},
    {"name": "潜渊墨龙", "rarity": "SSR", "supply": 1, "remain": 1, "power": 300},
    {"name": "祥云瑞龙", "rarity": "SSR", "supply": 1, "remain": 1, "power": 285},

    # ======================
    # 🧩 碎片卡（手动补全）
    # ======================

    {"name": "机敏灵鼠碎片", "rarity": "N", "supply": 6, "remain": 6, "power": 8},
    {"name": "仓廪实鼠碎片", "rarity": "N", "supply": 6, "remain": 6, "power": 9},
    {"name": "子夜神鼠碎片", "rarity": "N", "supply": 6, "remain": 6, "power": 9},

    {"name": "勤耕老牛碎片", "rarity": "N", "supply": 6, "remain": 6, "power": 10},
    {"name": "力拔山牛碎片", "rarity": "N", "supply": 6, "remain": 6, "power": 10},
    {"name": "丑时金牛碎片", "rarity": "N", "supply": 6, "remain": 6, "power": 11},

    {"name": "威猛猛虎碎片", "rarity": "N", "supply": 6, "remain": 6, "power": 11},
    {"name": "山林霸虎碎片", "rarity": "N", "supply": 6, "remain": 6, "power": 11},
    {"name": "寅虎啸月碎片", "rarity": "N", "supply": 6, "remain": 6, "power": 12},

    {"name": "娇小玉兔碎片", "rarity": "N", "supply": 6, "remain": 6, "power": 10},
    {"name": "月宫灵兔碎片", "rarity": "N", "supply": 6, "remain": 6, "power": 10},
    {"name": "卯兔衔芝碎片", "rarity": "N", "supply": 6, "remain": 6, "power": 11},

    {"name": "腾云驾蛇碎片", "rarity": "R", "supply": 6, "remain": 6, "power": 13},
    {"name": "玄冥灵蛇碎片", "rarity": "R", "supply": 6, "remain": 6, "power": 14},
    {"name": "巳蛇吐珠碎片", "rarity": "R", "supply": 6, "remain": 6, "power": 14},

    {"name": "骏逸天马碎片", "rarity": "R", "supply": 6, "remain": 6, "power": 15},
    {"name": "逐日无影马碎片", "rarity": "R", "supply": 6, "remain": 6, "power": 15},
    {"name": "午马扬蹄碎片", "rarity": "R", "supply": 6, "remain": 6, "power": 16},

    {"name": "温顺祥羊碎片", "rarity": "R", "supply": 6, "remain": 6, "power": 13},
    {"name": "瑞气羊驼碎片", "rarity": "R", "supply": 6, "remain": 6, "power": 13},
    {"name": "未羊献瑞碎片", "rarity": "R", "supply": 6, "remain": 6, "power": 13},

    {"name": "灵敏金猴碎片", "rarity": "SR", "supply": 6, "remain": 6, "power": 19},
    {"name": "斗战圣猴碎片", "rarity": "SR", "supply": 6, "remain": 6, "power": 21},
    {"name": "申猴戏果碎片", "rarity": "SR", "supply": 6, "remain": 6, "power": 19},

    {"name": "报晓金鸡碎片", "rarity": "SR", "supply": 6, "remain": 6, "power": 18},
    {"name": "凤鸣朝阳鸡碎片", "rarity": "SR", "supply": 6, "remain": 6, "power": 18},
    {"name": "酉鸡司晨碎片", "rarity": "SR", "supply": 6, "remain": 6, "power": 18},

    {"name": "忠诚义狗碎片", "rarity": "SR", "supply": 6, "remain": 6, "power": 20},
    {"name": "镇宅神犬碎片", "rarity": "SR", "supply": 6, "remain": 6, "power": 20},
    {"name": "戌狗守夜碎片", "rarity": "SR", "supply": 6, "remain": 6, "power": 19},

    {"name": "玄武黑猪碎片", "rarity": "SSR", "supply": 6, "remain": 6, "power": 25},
    {"name": "亥猪拱宝碎片", "rarity": "SSR", "supply": 6, "remain": 6, "power": 26},
    {"name": "福运肥猪碎片", "rarity": "SSR", "supply": 6, "remain": 6, "power": 25},

    {"name": "九天神龙碎片", "rarity": "UR", "supply": 6, "remain": 6, "power": 38},
    {"name": "哪吒闹海碎片", "rarity": "UR", "supply": 6, "remain": 6, "power": 36},
    {"name": "辰龙吟啸碎片", "rarity": "UR", "supply": 6, "remain": 6, "power": 40},

    {"name": "五爪金龙碎片", "rarity": "SSR", "supply": 6, "remain": 6, "power": 29},
    {"name": "烛龙烛九阴碎片", "rarity": "SSR", "supply": 6, "remain": 6, "power": 31},
    {"name": "青龙镇东方碎片", "rarity": "SSR", "supply": 6, "remain": 6, "power": 29},
    {"name": "赤焰火龙碎片", "rarity": "SSR", "supply": 6, "remain": 6, "power": 30},
    {"name": "潜渊墨龙碎片", "rarity": "SSR", "supply": 6, "remain": 6, "power": 30},
    {"name": "祥云瑞龙碎片", "rarity": "SSR", "supply": 6, "remain": 6, "power": 28},
]

def init_default_cards(session):
    """自动初始化牌库"""
    if session.query(Card).first():
        return
    
    print("正在创建内置十二生肖牌库...")
    for data in ZODIAC_CARDS:
        card = Card(
            name=data["name"],
            rarity=data["rarity"],
            supply=data["supply"],
            remain=data["remain"],
            power=data.get("power", 100)   # ← 新增这一行
        )
        session.add(card)
    
    session.commit()
    print(f"✅ 内置牌库创建完成！共 {len(ZODIAC_CARDS)} 张卡牌")

# ====================== 修仙境界系统 ======================
REALMS = [
    "炼气期", "筑基期", "结丹期", "元婴期", "化神期",
    "炼虚期", "合体期", "大乘期", "渡劫期", "飞升期", "仙帝"
]

STAGES = ["初期", "中期", "后期"]

def get_realm_name(level: int) -> str:
    """数字等级 → 修仙境界名称"""
    if level < 1:
        return "凡人"
    
    realm_index = (level - 1) // 3
    stage_index = (level - 1) % 3
    
    if realm_index >= len(REALMS):
        return "仙帝·圆满"
    
    return f"{REALMS[realm_index]}{STAGES[stage_index]}"
