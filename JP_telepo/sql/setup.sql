--sql
-- Get-Content sql/setup.sql | docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm
-- ==============================
-- 1. EXTENSIONS
-- ==============================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS hstore;

-- ==============================
-- 2. INDEXES (CRITICAL)
-- ==============================

-- For station filtering
CREATE INDEX IF NOT EXISTS idx_planet_osm_point_railway
ON planet_osm_point (railway);

-- For spatial queries
CREATE INDEX IF NOT EXISTS idx_planet_osm_point_way
ON planet_osm_point
USING GIST (way);

CREATE INDEX IF NOT EXISTS idx_planet_osm_polygon_way
ON planet_osm_polygon
USING GIST (way);

-- ==============================
-- 3. TOKYO STATIONS TABLE
-- ==============================

DROP TABLE IF EXISTS tokyo_stations;

CREATE TABLE tokyo_stations AS
SELECT
    name,
    ST_Y(ST_Transform(way, 4326)) AS lat,
    ST_X(ST_Transform(way, 4326)) AS lon
FROM planet_osm_point
WHERE railway = 'station'
AND name IS NOT NULL;

-- Index for fast lookup
CREATE INDEX idx_tokyo_stations_name
ON tokyo_stations (name);

-- ==============================
-- 4. BUSINESS SEARCH TABLE
-- ==============================

DROP TABLE IF EXISTS tokyo_business_search;

CREATE TABLE tokyo_business_search AS
SELECT
    name,
    amenity,
    shop,
    COALESCE(tags->'addr:full', '') AS address,
    tags->'phone' AS phone,
    tags->'website' AS website,
    way
FROM planet_osm_point
WHERE (
    amenity IS NOT NULL
    OR shop IS NOT NULL
)
AND name IS NOT NULL;

-- ==============================
-- 5. BUSINESS INDEXES
-- ==============================

-- Spatial index
CREATE INDEX idx_business_way
ON tokyo_business_search
USING GIST (way);

-- Text search indexes
CREATE INDEX idx_business_name
ON tokyo_business_search (name);

CREATE INDEX idx_business_amenity
ON tokyo_business_search (amenity);

CREATE INDEX idx_business_shop
ON tokyo_business_search (shop);

-- Optional: phone filter
CREATE INDEX idx_business_phone
ON tokyo_business_search (phone);

-- ==============================
-- 6. FULL TEXT SEARCH (OPTIONAL BUT POWERFUL)
-- ==============================

ALTER TABLE tokyo_business_search
ADD COLUMN IF NOT EXISTS search_text tsvector;

UPDATE tokyo_business_search
SET search_text =
    to_tsvector('simple', coalesce(name,'') || ' ' || coalesce(amenity,'') || ' ' || coalesce(shop,''));

CREATE INDEX idx_business_search_text
ON tokyo_business_search
USING GIN (search_text);

-- ==============================
-- DONE
-- ==============================

-- Verify
SELECT COUNT(*) FROM tokyo_stations;
SELECT COUNT(*) FROM tokyo_business_search;
