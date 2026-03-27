-- 既存テーブルを削除（存在する場合）
DROP TABLE IF EXISTS tokyo_business_search;

-- ビジネス検索用テーブルを作成
CREATE TABLE tokyo_business_search AS

-- -----------------------------
-- ノード（ポイント）データの店舗・施設
-- -----------------------------
SELECT
    name,                         -- 名称
    amenity,                      -- 施設カテゴリ
    shop,                         -- 店舗種別
    tourism,                      -- 観光関連
    tags->'phone' AS phone,       -- 電話番号
    tags->'website' AS website,   -- ウェブサイト
    tags->'addr:housenumber' AS housenumber, -- 番地
    tags->'addr:street' AS street,            -- 通り名
    way                           -- 位置情報（ポイント）
FROM planet_osm_point
WHERE name IS NOT NULL
AND (
    amenity IS NOT NULL
    OR shop IS NOT NULL
    OR tourism IS NOT NULL
)

UNION ALL

-- -----------------------------
-- 建物（ポリゴン）データの店舗・施設
-- -----------------------------
SELECT
    name,                         -- 名称
    amenity,                      -- 施設カテゴリ
    shop,                         -- 店舗種別
    tourism,                      -- 観光関連
    tags->'phone' AS phone,       -- 電話番号
    tags->'website' AS website,   -- ウェブサイト
    tags->'addr:housenumber' AS housenumber, -- 番地
    tags->'addr:street' AS street,            -- 通り名
    ST_Centroid(way) AS way       -- ポリゴンの中心点を取得
FROM planet_osm_polygon
WHERE name IS NOT NULL
AND (
    amenity IS NOT NULL
    OR shop IS NOT NULL
    OR tourism IS NOT NULL
);