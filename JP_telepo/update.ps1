Write-Host "🚀 Updating OSM..."
docker exec tokyo_osm_updater osm2pgsql-replication update -d tokyo_osm -H postgis -U postgres

Write-Host "📊 Refreshing table..."
Get-Content sql/refresh_business_table.sql | docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm

Write-Host "✅ Done"