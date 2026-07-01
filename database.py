from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from config import DATABASE_URL
import logging

Base = declarative_base()

# 创建数据库引擎
if DATABASE_URL and DATABASE_URL.startswith("postgres"):
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=300,
    )
    logging.info("✅ 使用 PostgreSQL 数据库")
else:
    engine = create_engine(
        DATABASE_URL or "sqlite:///game.db",
        pool_pre_ping=True,
    )
    logging.info("✅ 使用 SQLite 数据库")

Session = sessionmaker(bind=engine)

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Database error: {e}")
        raise
    finally:
        session.close()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
    
    # 自动初始化牌库
    with get_session() as s:
        models.init_default_cards(s)
