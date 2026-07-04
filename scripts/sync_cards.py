from database import get_session
from models import Card
from your_file import ZODIAC_CARDS


def sync_cards_to_db():
    with get_session() as s:

        added = 0

        for c in ZODIAC_CARDS:

            # 如果已存在就跳过
            exists = s.query(Card).filter(Card.name == c["name"]).first()
            if exists:
                continue

            card = Card(
                name=c["name"],
                rarity=c["rarity"],
                supply=c["supply"],
                remain=c["remain"],
                power=c["power"]
            )

            s.add(card)
            added += 1

        s.commit()

        print(f"新增卡牌完成：{added} 张")


if __name__ == "__main__":
    sync_cards_to_db()
