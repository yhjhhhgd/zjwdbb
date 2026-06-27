from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.ext.mutable import MutableDict
from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String)

    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)

    coins = Column(Integer, default=100)
    qi = Column(Integer, default=0)
    luck = Column(Float, default=1.0)

    last_msg = Column(Integer, default=0)
    last_drop = Column(Integer, default=0)

    cards = Column(MutableDict.as_mutable(JSON), default=dict)

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
