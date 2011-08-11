#! /bin/bash

. ./draw-functions.sh

cd $WORKDIR/images

# coastline
get_line_shp coastline.shp "tags ? 'natural' AND tags->'natural' = 'coastline'"

# border
get_line_shp border.shp "tags ? 'admin_level' AND tags->'admin_level' = '2' AND NOT tags ? 'maritime'"
# admin_level
get_line_shp admin_4.shp "tags ? 'admin_level' AND tags->'admin_level' = '4' AND NOT tags ? 'maritime'"
get_line_shp admin_6.shp "tags ? 'admin_level' AND tags->'admin_level' = '6' AND NOT tags ? 'maritime'"

# rivers
get_line_shp rivers_line.shp "tags ? 'waterway' AND tags->'waterway' != 'stream'"
get_polygon_shp rivers_polygon.shp "tags ? 'waterway' AND tags->'waterway' != 'stream'"
get_polygon_shp rivers_lake.shp "(tags ? 'natural' AND tags->'natural' = 'water' OR tags ? 'landuse' AND tags->'landuse' = 'reservoir') AND
                             ST_Area(geography(ST_MakePolygon(linestring))) > 100"

# relation rivers
pgsql2shp -f rivers-relation.shp "$DATABASE" "
SELECT member_id, way_geom(member_id) AS geom
FROM relations
JOIN relation_members ON relations.id = relation_members.relation_id AND
                         relation_members.member_role != 'waterbank' AND
                         relation_members.member_role != 'tributary' AND
                         relation_members.member_type = 'W'
WHERE tags->'type' = 'waterway' AND
      ST_GeometryType(way_geom(member_id)) = 'ST_LineString' AND
      ST_NumPoints(way_geom(member_id)) > 2
ORDER BY relations.id, relation_members.sequence_id;"

pgsql2shp -f rivers-relation-tributary.shp "$DATABASE" "
SELECT member_id, way_geom(member_id) AS geom
FROM relations
JOIN relation_members ON relations.id = relation_members.relation_id AND
                         relation_members.member_role = 'tributary' AND
                         relation_members.member_type = 'W'
WHERE tags->'type' = 'waterway' AND
      ST_GeometryType(way_geom(member_id)) = 'ST_LineString' AND
      ST_NumPoints(way_geom(member_id)) > 2
ORDER BY relations.id, relation_members.sequence_id;"

# power lines
get_line_shp power.shp "tags->'power' = 'line'"

# motorway
get_line_shp motorway.shp "tags ? 'highway' AND tags->'highway' = 'motorway'"
