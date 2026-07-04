import random
from models import Card

# ====================== 价格区间配置 ======================
PRICE_RANGES = {
    "N": (1000, 2000),
    "R": (2600, 4000),
    "SR": (4600, 7000),
    "SSR": (8000, 16000),
    "UR": (18000, 35000),
    "NR": (25000, 56000)
}


def calc_price(rarity: str) -> int:
    """根据稀有度计算价格"""
    if rarity == "NR":
        return random.randint(15000, 99999)
    
    min_p, max_p = PRICE_RANGES.get(rarity, (1000, 2000))
    base_price = random.randint(min_p, max_p)
    
    # 🔥 修改为 ±20% 大波动
    final_price = int(base_price * random.uniform(0.80, 1.20))
    
    return max(500, final_price)


def get_zodiac_name(card_name: str) -> str:
    """从卡牌名称提取生肖"""
    zodiac_map = {
        "鼠": "鼠", "牛": "牛", "虎": "虎", "兔": "兔",
        "龙": "龙", "蛇": "蛇", "马": "马", "羊": "羊",
        "猴": "猴", "鸡": "鸡", "狗": "狗", "猪": "猪"
    }
    for z in zodiac_map:
        if z in card_name:
            return zodiac_map[z]
    return "其他"


def update_market(session):
    """刷新行情（目前无需持久化）"""
    pass


def get_zodiac_overview(session):
    """12生肖 + NR 整体行情概览"""
    cards = session.query(Card).all()
    if not cards:
        return "暂无卡牌数据"

    zodiac_data = {}
    nr_prices = []

    for card in cards:
        price = calc_price(card.rarity)
        zodiac = get_zodiac_name(card.name)
        
        if zodiac not in zodiac_data:
            zodiac_data[zodiac] = []
        zodiac_data[zodiac].append(price)
        
        if card.rarity in ["NR", "UR"]:   # NR 和 UR 归入高波动
            nr_prices.append(price)

    result = "📊 **12生肖行情总览**（实时·大波动）\n\n"
    
    for z in ["鼠","牛","虎","兔","龙","蛇","马","羊","猴","鸡","狗","猪"]:
        if z in zodiac_data and zodiac_data[z]:
            prices = zodiac_data[z]
            avg = sum(prices) // len(prices)
            change = random.uniform(-8, 8)   # 整体概览波动稍小
            arrow = "📈" if change > 0 else "📉"
            result += f"{arrow} {z}  {avg:,}  {change:+.1f}%\n"
        else:
            result += f"➖ {z}  ———\n"

    # 高阶卡独立行情
    if nr_prices:
        nr_avg = sum(nr_prices) // len(nr_prices)
        nr_change = random.uniform(-12, 12)
        result += f"\n🔴 **NR / UR 高阶区**  {nr_avg:,}  {nr_change:+.1f}%\n"

    result += "\n💡 使用 `/hq 鼠` 查看单个生肖详细"
    return result


def get_zodiac_detail(session, zodiac: str):
    """单个生肖详细行情（20% 大波动）"""
    cards = session.query(Card).filter(Card.name.like(f"%{zodiac}%")).all()
    
    if not cards:
        return f"❌ 未找到 “{zodiac}” 相关卡牌"

    result = f"🐾 **{zodiac} 生肖行情**（实时波动）\n\n"
    
    for card in cards:
        price = calc_price(card.rarity)
        change = random.uniform(-20, 20)
        arrow = "📈" if change >= 0 else "📉"
        
        result += (
            f"🃏 {card.name}\n"
            f"💰 {price:,} 金币\n"
            f"{arrow} {change:+.1f}%\n"
            f"⭐ {card.rarity}\n\n"
        )
    
    return result
