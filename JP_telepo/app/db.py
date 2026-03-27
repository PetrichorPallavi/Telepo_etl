# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Docker上のPostgreSQL（関東OSMデータ）
DATABASE_URL = "postgresql+psycopg://postgres:postgres@127.0.0.1:5433/tokyo_osm"

# UTF-8エンコーディングを強制
engine = create_engine(
    DATABASE_URL,
    connect_args={"client_encoding": "UTF8"},
    # encoding='CP932'  # 必要に応じてWindows用エンコーディング
    pool_pre_ping=True,
    future=True
)

# セッション作成（オプション）
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)