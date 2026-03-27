# app/queries.py
from sqlalchemy import create_engine, text

# PostgreSQL（東京OSMデータベース）に接続
engine = create_engine(
    "postgresql+psycopg://postgres:postgres@127.0.0.1:5433/tokyo_osm"
)

# -----------------------------
# 東京の駅一覧を取得
# -----------------------------
def get_tokyo_stations():
    sql = text("""
        SELECT
            name,
            ST_Y(ST_Transform(way, 4326)) AS lat,
            ST_X(ST_Transform(way, 4326)) AS lon
        FROM planet_osm_point
        WHERE railway = 'station'
          AND name IS NOT NULL
        ORDER BY name;
    """)
    with engine.connect() as conn:
        return conn.execute(sql).fetchall()


# -----------------------------
# 指定条件で店舗・施設を検索
# -----------------------------
def search_places(search_term, lat, lon, radius, offset=0):
    sql = text("""
        WITH center AS (
            SELECT ST_Transform(
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                3857
            ) AS geom
        )

        SELECT
            name,
            amenity,
            shop,
            housenumber || ' ' || street AS address,
            phone,
            website, 
            ST_Y(ST_Transform(way, 4326)) AS lat,
            ST_X(ST_Transform(way, 4326)) AS lon, 
            ST_Distance(way, center.geom) AS distance
               
        FROM tokyo_business_search, center
        WHERE (
            name ILIKE :term OR
            amenity ILIKE :term OR
            shop ILIKE :term
        )
        AND ST_DWithin(
               way, 
               center.geom, 
               :radius
            )
        AND phone IS NOT NULL      
        ORDER BY distance
        LIMIT 200 OFFSET :offset;
    """)

    with engine.connect() as conn:
        return conn.execute(sql, {
            "term": f"%{search_term}%",
            "lon": lon,
            "lat": lat,
            "radius": radius,
            "offset": offset
        }).fetchall()