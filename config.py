import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(i) for i in os.getenv("ADMIN_IDS", "").split(",") if i]

# 🔥 PostgreSQL 配置（优先使用环境变量）
DATABASE_URL = os.getenv("DATABASE_URL")

# 本地开发备用（如果没有设置环境变量就用 SQLite）
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///game.db"

print(f"当前使用数据库: {'PostgreSQL' if 'postgres' in DATABASE_URL else 'SQLite'}")
