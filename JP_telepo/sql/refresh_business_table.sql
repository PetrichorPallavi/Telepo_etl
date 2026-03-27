TRUNCATE tokyo_business_search;

INSERT INTO tokyo_business_search
SELECT
    name,
    tags->'amenity' AS amenity,
    tags->'shop' AS shop,
    tags->'phone' AS phone,
    tags->'website' AS website,
    way
FROM planet_osm_point
WHERE name IS NOT NULL;