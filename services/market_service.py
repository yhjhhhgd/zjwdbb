import random
from models import Card

# ====================== 统一价格表（已提升5倍，你自定义的版本） ======================
PRICE_TABLE = {
    # N级
    "机敏灵鼠": (3250, 6250), "仓廪实鼠": (3400, 6400), "子夜神鼠": (2500, 6600),
    "勤耕老牛": (4250, 7750), "力拔山牛": (4400, 7100), "丑时金牛": (4600, 7400),
    "威猛猛虎": (5250, 8500), "山林霸虎": (5400, 8750), "寅虎啸月": (5600, 8250),
    "娇小玉兔": (6100, 9600), "月宫灵兔": (6250, 10900), "卯兔衔芝": (7400, 11100),
    
    # R级
    "腾云驾蛇": (8250, 15500), "玄冥灵蛇": (8750, 17250), "巳蛇吐珠": (8250, 16250),
    "骏逸天马": (7750, 13000), "逐日无影马": (8250, 14000), "午马扬蹄": (8750, 14750),
    "温顺祥羊": (5900, 13900), "瑞气羊驼": (6100, 15250), "未羊献瑞": (9400, 17750),
    
    # SR级
    "灵敏金猴": (16000, 26000), "斗战圣猴": (19000, 31000), "申猴戏果": (17000, 27500),
    "报晓金鸡": (15500, 25500), "凤鸣朝阳鸡": (16250, 26500), "酉鸡司晨": (15900, 26250),
    "忠诚义狗": (18000, 29000), "镇宅神犬": (18500, 30000), "戌狗守夜": (17750, 28750),
    
    # SSR级
    "玄武黑猪": (42500, 67500), "亥猪拱宝": (46000, 74000), "福运肥猪": (44000, 71000),
    
    # UR级
    "九天神龙": (142500, 192500), "哪吒闹海": (154000, 282500), "辰龙吟啸": (140000, 265000),
    "五爪金龙": (67500, 117500), "烛龙烛九阴": (52500, 127500),
    "青龙镇东方": (59000, 121000), "赤焰火龙": (61000, 94000),
    "潜渊墨龙": (50000, 110000), "祥云瑞龙": (76000, 98000),
}


def get_card_price(card_name: str):
    if card_name in PRICE_TABLE:
        min_p, max_p = PRICE_TABLE[card_name]
        return random.randint(min_p, max_p)
    return random.randint(2000, 5000)


def get_all_cards(session):
    """返回所有卡牌数据供分页使用"""
    return session.query(Card).order_by(Card.rarity.desc(), Card.id).all()


def get_market_page(session, page: int = 1):
    """分页详细列表（显示卡牌ID）"""
    cards = get_all_cards(session)
    page_size = 8
    total_pages = (len(cards) + page_size - 1) // page_size
    page = max(1, min(page, total_pages))
    
    start = (page - 1) * page_size
    end = start + page_size
    page_cards = cards[start:end]

    result = f"📊 **生肖卡牌行情** 第 {page}/{total_pages} 页\n\n"
    
    for card in page_cards:
        price = get_card_price(card.name)
        result += f"🆔 **ID: {card.id}** | 🃏 {card.name} | 💰 `{price:,}` | 剩余 `{card.remain}` | ⭐{card.rarity}\n"
    
    result += f"\n💡 用 `/buy <ID> <数量>` 购买，例如：/buy 5 1\n"
    result += f"`/market {page+1 if page < total_pages else 1}` 翻页"
    return result


def get_zodiac_overview(session):
    """大盘概览（供 /hq 使用）"""
    cards = get_all_cards(session)
    if not cards:
        return "暂无卡牌数据"

    zodiac_data = {}
    for card in cards:
        price = get_card_price(card.name)
        zodiac = next((z for z in ["鼠","牛","虎","兔","龙","蛇","马","羊","猴","鸡","狗","猪"] if z in card.name), "其他")
        if zodiac not in zodiac_data:
            zodiac_data[zodiac] = []
        zodiac_data[zodiac].append(price)

    result = "📊 **生肖卡牌大盘行情**（独家数据）\n\n"
    
    for z in ["鼠","牛","虎","兔","龙","蛇","马","羊","猴","鸡","狗","猪"]:
        if z in zodiac_data and zodiac_data[z]:
            avg = sum(zodiac_data[z]) // len(zodiac_data[z])
            change = random.uniform(-12, 12)
            arrow = "📈" if change >= 0 else "📉"
            result += f"{arrow} **{z}**  {avg:,}  {change:+.1f}%\n"
        else:
            result += f"➖ **{z}**  ———\n"

    result += "\n💡 /market 查看详细列表 | /buy <ID> <数量> 购买 | /sell <ID> <数量> 卖出"
    return result
