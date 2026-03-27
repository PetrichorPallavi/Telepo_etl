DROP TABLE IF EXISTS tokyo_business_search;

CREATE TABLE tokyo_business_search AS

-- Node businesses
SELECT
    name,
    amenity,
    shop,
    tourism,
    tags->'phone' AS phone,
    tags->'website' AS website,
    tags->'addr:housenumber' AS housenumber,
    tags->'addr:street' AS street,
    way
FROM planet_osm_point
WHERE name IS NOT NULL
AND (
    amenity IS NOT NULL
    OR shop IS NOT NULL
    OR tourism IS NOT NULL
)

UNION ALL

-- Building businesses
SELECT
    name,
    amenity,
    shop,
    tourism,
    tags->'phone' AS phone,
    tags->'website' AS website,
    tags->'addr:housenumber' AS housenumber,
    tags->'addr:street' AS street,
    ST_Centroid(way) AS way
FROM planet_osm_polygon
WHERE name IS NOT NULL
AND (
    amenity IS NOT NULL
    OR shop IS NOT NULL
    OR tourism IS NOT NULL
);