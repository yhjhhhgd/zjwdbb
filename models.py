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


class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    rarity = Column(String)
    supply = Column(Integer)
    remain = Column(Integer)


class Market(Base):
    __tablename__ = "market"
    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer)
    card_id = Column(Integer)
    price = Column(Integer)
    amount = Column(Integer)
    created_at = Column(Integer)


# ====================== 内置牌库 ======================
ZODIAC_CARDS = [
    {"name": "机敏灵鼠", "rarity": "N", "supply": 800, "remain": 800},
    {"name": "仓廪实鼠", "rarity": "N", "supply": 750, "remain": 750},
    {"name": "子夜神鼠", "rarity": "N", "supply": 700, "remain": 700},
    {"name": "勤耕老牛", "rarity": "N", "supply": 780, "remain": 780},
    {"name": "力拔山牛", "rarity": "N", "supply": 720, "remain": 720},
    {"name": "丑时金牛", "rarity": "N", "supply": 690, "remain": 690},
    {"name": "威猛猛虎", "rarity": "N", "supply": 760, "remain": 760},
    {"name": "山林霸虎", "rarity": "N", "supply": 710, "remain": 710},
    {"name": "寅虎啸月", "rarity": "N", "supply": 680, "remain": 680},
    {"name": "娇小玉兔", "rarity": "N", "supply": 740, "remain": 740},
    {"name": "月宫灵兔", "rarity": "N", "supply": 700, "remain": 700},
    {"name": "卯兔衔芝", "rarity": "N", "supply": 670, "remain": 670},
    
    # R级
    {"name": "腾云驾蛇", "rarity": "R", "supply": 450, "remain": 450},
    {"name": "玄冥灵蛇", "rarity": "R", "supply": 420, "remain": 420},
    {"name": "巳蛇吐珠", "rarity": "R", "supply": 400, "remain": 400},
    {"name": "骏逸天马", "rarity": "R", "supply": 460, "remain": 460},
    {"name": "逐日无影马", "rarity": "R", "supply": 430, "remain": 430},
    {"name": "午马扬蹄", "rarity": "R", "supply": 410, "remain": 410},
    {"name": "温顺祥羊", "rarity": "R", "supply": 440, "remain": 440},
    {"name": "瑞气羊驼", "rarity": "R", "supply": 415, "remain": 415},
    {"name": "未羊献瑞", "rarity": "R", "supply": 395, "remain": 395},
    
    # SR级
    {"name": "灵敏金猴", "rarity": "SR", "supply": 280, "remain": 280},
    {"name": "斗战圣猴", "rarity": "SR", "supply": 260, "remain": 260},
    {"name": "申猴戏果", "rarity": "SR", "supply": 240, "remain": 240},
    {"name": "报晓金鸡", "rarity": "SR", "supply": 270, "remain": 270},
    {"name": "凤鸣朝阳鸡", "rarity": "SR", "supply": 250, "remain": 250},
    {"name": "酉鸡司晨", "rarity": "SR", "supply": 230, "remain": 230},
    {"name": "忠诚义狗", "rarity": "SR", "supply": 265, "remain": 265},
    {"name": "镇宅神犬", "rarity": "SR", "supply": 245, "remain": 245},
    {"name": "戌狗守夜", "rarity": "SR", "supply": 225, "remain": 225},
    
    # SSR级
    {"name": "玄武黑猪", "rarity": "SSR", "supply": 120, "remain": 120},
    {"name": "亥猪拱宝", "rarity": "SSR", "supply": 110, "remain": 110},
    {"name": "福运肥猪", "rarity": "SSR", "supply": 100, "remain": 100},
    
    # 龙最稀有
    {"name": "九天神龙", "rarity": "UR", "supply": 25, "remain": 25},
    {"name": "哪吒闹海", "rarity": "UR", "supply": 20, "remain": 20},
    {"name": "辰龙吟啸", "rarity": "UR", "supply": 18, "remain": 18},
    {"name": "五爪金龙", "rarity": "SSR", "supply": 80, "remain": 80},
    {"name": "烛龙烛九阴", "rarity": "SSR", "supply": 65, "remain": 65},
    {"name": "青龙镇东方", "rarity": "SSR", "supply": 55, "remain": 55},
    {"name": "赤焰火龙", "rarity": "SSR", "supply": 70, "remain": 70},
    {"name": "潜渊墨龙", "rarity": "SSR", "supply": 60, "remain": 60},
    {"name": "祥云瑞龙", "rarity": "SSR", "supply": 75, "remain": 75},
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
