#! /bin/bash

. ./draw-functions.sh

pgsql2shp -f france-sandre.shp osm "
SELECT member_id, way_geom(member_id) AS geom
FROM relation_tags
JOIN relation_members ON relation_tags.relation_id = relation_members.relation_id AND
                         relation_members.member_role != 'waterbank' AND
                         relation_members.member_type = 'W'
WHERE k = 'ref:sandre' AND
      ST_GeometryType(way_geom(member_id)) = 'ST_LineString' AND
      ST_NumPoints(way_geom(member_id)) > 2
ORDER BY relation_tags.relation_id, relation_members.sequence_id;"

./create_tif.py france-coastline.shp france-sandre-rivers.tif

gdal_rasterize -b 1 -burn 255 -l france-sandre france-sandre.shp france-sandre-rivers.tif
draw_shp france-sandre-rivers.tif france-coastline.shp 200 200 255

gdal_rasterize -b 1 -burn 255 -l france-sandre france-sandre.shp france-rivers.tif
draw_shp france-rivers.tif france-border.shp 200 200 0
draw_shp france-rivers.tif france-coastline.shp 200 200 255
