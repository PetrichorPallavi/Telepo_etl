from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg://postgres:postgres@127.0.0.1:5433/tokyo_osm",
    pool_pre_ping=True
)

# -------------------------
# Stations (FAST - precomputed)
# -------------------------
def get_tokyo_stations():
    sql = text("""
        SELECT name, lat, lon
        FROM tokyo_stations
        ORDER BY name
    """)
    with engine.connect() as conn:
        return conn.execute(sql).fetchall()


# -------------------------
# Business Search (Optimized)
# -------------------------
def search_places(search_term, lat, lon, radius, limit=50, offset=0):
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
            address,
            phone,
            website,
            ST_Y(ST_Transform(way, 4326)) AS lat,
            ST_X(ST_Transform(way, 4326)) AS lon,
            ST_Distance(way, center.geom) AS distance
        FROM tokyo_business_search, center
        WHERE (
            search_text @@ plainto_tsquery('simple', :term)
            OR name ILIKE :like_term
        )
        AND ST_DWithin(way, center.geom, :radius)
        and (phone IS NOT NULL AND phone != '')       
        ORDER BY distance
        LIMIT :limit OFFSET :offset
    """)

    with engine.connect() as conn:
        return conn.execute(sql, {
            "term": search_term,
            "like_term": f"%{search_term}%",
            "lat": lat,
            "lon": lon,
            "radius": radius,
            "limit": limit,
            "offset": offset
        }).fetchall()
