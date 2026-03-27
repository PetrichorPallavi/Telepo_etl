# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Docker Postgres with Kanto OSM data
DATABASE_URL = "postgresql+psycopg://postgres:postgres@127.0.0.1:5433/tokyo_osm"

# Force UTF-8 encoding
engine = create_engine(
    DATABASE_URL,
    connect_args={"client_encoding": "UTF8"},
    # encoding='CP932'
    pool_pre_ping=True,
    future=True
)

# Optional: create session
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)