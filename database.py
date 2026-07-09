from sqlalchemy import text   # ← 在文件顶部添加这
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
    
    with get_session() as s:
        # ==================== 安全添加字段 ====================
        try:
            s.execute(text("ALTER TABLE cards ADD COLUMN IF NOT EXISTS power INTEGER DEFAULT 100"))
            s.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS pk_count_today INTEGER DEFAULT 0"))
            s.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_pk_date INTEGER DEFAULT 0"))
            
            # 新增：市场交易冷却时间
            s.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_market_action BIGINT DEFAULT 0"))
            s.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_buy_action BIGINT DEFAULT 0"))
            s.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_sell_action BIGINT DEFAULT 0"))
            
            print("✅ 数据库字段添加成功（或已存在）")
        except Exception as e:
            print(f"字段添加提示: {e}")

        try:
            s.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS inviter_id BIGINT"))
            s.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS invited_count INTEGER DEFAULT 0"))
            print("✅ 师徒字段添加成功")
        except Exception as e:
            print(f"字段添加提示: {e}")
        try:
            s.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS sect_id INTEGER"))
            s.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS sect_role VARCHAR"))
            s.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS contribution INTEGER DEFAULT 0"))
            print("✅ 宗门系统字段添加成功")
        except Exception as e:
            print(f"宗门字段提示: {e}")
        
        # 初始化牌库
        models.init_default_cards(s)
