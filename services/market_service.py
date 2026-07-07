import random
import time
from models import Card

# ====================== 全局价格缓存（60秒刷新） ======================
price_cache = {}
last_refresh = 0
CACHE_DURATION = 10   # 每60秒刷新一次

# ====================== 统一价格表（已提升5倍） ======================
PRICE_TABLE = {
    "机敏灵鼠": (4250, 5250), "仓廪实鼠": (5400, 6400), "子夜神鼠": (5500, 6600),
    "勤耕老牛": (6250, 7750), "力拔山牛": (4800, 6100), "丑时金牛": (5100, 6400),
    "威猛猛虎": (7150, 8500), "山林霸虎": (7800, 8750), "寅虎啸月": (6900, 8250),
    "娇小玉兔": (8100, 9600), "月宫灵兔": (8750, 10900), "卯兔衔芝": (9400, 11100),
    
    "腾云驾蛇": (12500, 15500), "玄冥灵蛇": (14750, 17250), "巳蛇吐珠": (15250, 16250),
    "骏逸天马": (11750, 13000), "逐日无影马": (12250, 14000), "午马扬蹄": (12750, 14750),
    "温顺祥羊": (12900, 13900), "瑞气羊驼": (14100, 15250), "未羊献瑞": (15400, 17750),
    
    "灵敏金猴": (23000, 26000), "斗战圣猴": (27000, 31000), "申猴戏果": (25000, 27500),
    "报晓金鸡": (23500, 25500), "凤鸣朝阳鸡": (23250, 26500), "酉鸡司晨": (23900, 26250),
    "忠诚义狗": (24900, 29000), "镇宅神犬": (25500, 30000), "戌狗守夜": (25750, 28750),
    
    "玄武黑猪": (59500, 67500), "亥猪拱宝": (68000, 74000), "福运肥猪": (65000, 71000),
    
    "九天神龙": (142500, 162500), "哪吒闹海": (188000, 282500), "辰龙吟啸": (140000, 185000),
    "五爪金龙": (67500, 87500), "烛龙烛九阴": (82500, 97500),
    "青龙镇东方": (59000, 71000), "赤焰火龙": (71000, 84000),
    "潜渊墨龙": (70000, 80000), "祥云瑞龙": (79000, 98000),
}


def get_card_price(card_name: str):
    global last_refresh
    
    now = int(time.time())
    if now - last_refresh > CACHE_DURATION:
        price_cache.clear()
        last_refresh = now
        print(f"【行情】价格缓存已刷新 ({now})")

    if card_name not in price_cache:
        if card_name in PRICE_TABLE:
            min_p, max_p = PRICE_TABLE[card_name]
            price_cache[card_name] = random.randint(min_p, max_p)
        else:
            price_cache[card_name] = random.randint(3000, 5000)
    
    return price_cache[card_name]


def get_all_cards(session):
    return session.query(Card).order_by(Card.rarity.desc(), Card.id).all()


def get_market_page(session, page: int = 1):
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
    
    result += f"\n💡 用 /buy <ID> <数量> 购买，例如：/buy 5 1\n"
    result += f"/market {page+1 if page < total_pages else 1} 翻页"
    return result


def get_zodiac_overview(session):
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

    result = "📊 **生肖卡牌大盘行情**（精准打击）\n\n"
    
    for z in ["鼠","牛","虎","兔","龙","蛇","马","羊","猴","鸡","狗","猪"]:
        if z in zodiac_data and zodiac_data[z]:
            avg = sum(zodiac_data[z]) // len(zodiac_data[z])
            change = random.uniform(-15, 8)
            arrow = "📈" if change >= 0 else "📉"
            result += f"{arrow} **{z}**  {avg:,}  {change:+.1f}%\n"
        else:
            result += f"➖ **{z}**  ———\n"

    result += "\n💡 /market 查看详细列表 | /buy <ID> <数量> 购买 | /sell <ID> <数量> 卖出"
    return result
