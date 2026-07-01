from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from config import DATABASE_URL

Base = declarative_base()

# 根据数据库类型调整参数
if DATABASE_URL.startswith("postgres"):
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=300,      # PostgreSQL 推荐
    )
else:
    # SQLite 本地开发
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )

Session = sessionmaker(bind=engine)

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
    
    # 自动初始化牌库
    with get_session() as s:
        models.init_default_cards(s)
