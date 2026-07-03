from sqlalchemy import Column, Integer, String, Float, JSON, BigInteger   # ← 添加 BigInteger
from sqlalchemy.ext.mutable import MutableDict
from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)   # ← 改成 BigInteger
    username = Column(String)

    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)

    coins = Column(Integer, default=100)
    qi = Column(Integer, default=0)
    luck = Column(Float, default=1.0)

    last_msg = Column(Integer, default=0)
    last_drop = Column(Integer, default=0)

    cards = Column(
        MutableDict.as_mutable(JSON),
        default=dict
    )

    frozen = Column(Integer, default=0)
        # PK相关
    pk_count_today = Column(Integer, default=0)
    last_pk_date = Column(Integer, default=0)


class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    rarity = Column(String)
    supply = Column(Integer)
    remain = Column(Integer)
    power = Column(Integer, default=100)   # 卡牌强势值


class Market(Base):
    __tablename__ = "market"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    seller_id = Column(BigInteger)   # ⭐ 必改
    card_id = Column(BigInteger)     # ⭐ 建议也改
    price = Column(Integer)
    amount = Column(Integer)
    created_at = Column(BigInteger)  # ⭐ 建议改


# ====================== 内置牌库 ======================
ZODIAC_CARDS = [
    {"name": "机敏灵鼠", "rarity": "N", "supply": 5, "remain": 5},
    {"name": "仓廪实鼠", "rarity": "N", "supply": 5, "remain": 5},
    {"name": "子夜神鼠", "rarity": "N", "supply": 5, "remain": 5},

    {"name": "勤耕老牛", "rarity": "N", "supply": 3, "remain": 3},
    {"name": "力拔山牛", "rarity": "N", "supply": 3, "remain": 3},
    {"name": "丑时金牛", "rarity": "N", "supply": 3, "remain": 3},

    {"name": "威猛猛虎", "rarity": "N", "supply": 2, "remain": 2},
    {"name": "山林霸虎", "rarity": "N", "supply": 2, "remain": 2},
    {"name": "寅虎啸月", "rarity": "N", "supply": 2, "remain": 2},

    {"name": "娇小玉兔", "rarity": "N", "supply": 2, "remain": 2},
    {"name": "月宫灵兔", "rarity": "N", "supply": 2, "remain": 2},
    {"name": "卯兔衔芝", "rarity": "N", "supply": 2, "remain": 2},

    # R
    {"name": "腾云驾蛇", "rarity": "R", "supply": 1, "remain": 1},
    {"name": "玄冥灵蛇", "rarity": "R", "supply": 1, "remain": 1},
    {"name": "巳蛇吐珠", "rarity": "R", "supply": 1, "remain": 1},

    {"name": "骏逸天马", "rarity": "R", "supply": 1, "remain": 1},
    {"name": "逐日无影马", "rarity": "R", "supply": 1, "remain": 1},
    {"name": "午马扬蹄", "rarity": "R", "supply": 1, "remain": 1},

    {"name": "温顺祥羊", "rarity": "R", "supply": 1, "remain": 1},
    {"name": "瑞气羊驼", "rarity": "R", "supply": 1, "remain": 1},
    {"name": "未羊献瑞", "rarity": "R", "supply": 1, "remain": 1},

    # SR
    {"name": "灵敏金猴", "rarity": "SR", "supply": 1, "remain": 1},
    {"name": "斗战圣猴", "rarity": "SR", "supply": 1, "remain": 1},
    {"name": "申猴戏果", "rarity": "SR", "supply": 1, "remain": 1},

    {"name": "报晓金鸡", "rarity": "SR", "supply": 1, "remain": 1},
    {"name": "凤鸣朝阳鸡", "rarity": "SR", "supply": 1, "remain": 1},
    {"name": "酉鸡司晨", "rarity": "SR", "supply": 1, "remain": 1},

    {"name": "忠诚义狗", "rarity": "SR", "supply": 1, "remain": 1},
    {"name": "镇宅神犬", "rarity": "SR", "supply": 1, "remain": 1},
    {"name": "戌狗守夜", "rarity": "SR", "supply": 1, "remain": 1},

    # SSR
    {"name": "玄武黑猪", "rarity": "SSR", "supply": 1, "remain": 1},
    {"name": "亥猪拱宝", "rarity": "SSR", "supply": 1, "remain": 1},
    {"name": "福运肥猪", "rarity": "SSR", "supply": 1, "remain": 1},

    # UR
    {"name": "九天神龙", "rarity": "UR", "supply": 1, "remain": 1},
    {"name": "哪吒闹海", "rarity": "UR", "supply": 1, "remain": 1},
    {"name": "辰龙吟啸", "rarity": "UR", "supply": 1, "remain": 1},

    {"name": "五爪金龙", "rarity": "SSR", "supply": 1, "remain": 1},
    {"name": "烛龙烛九阴", "rarity": "SSR", "supply": 1, "remain": 1},
    {"name": "青龙镇东方", "rarity": "SSR", "supply": 1, "remain": 1},
    {"name": "赤焰火龙", "rarity": "SSR", "supply": 1, "remain": 1},
    {"name": "潜渊墨龙", "rarity": "SSR", "supply": 1, "remain": 1},
    {"name": "祥云瑞龙", "rarity": "SSR", "supply": 1, "remain": 1},
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
            remain=data["remain"]
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
