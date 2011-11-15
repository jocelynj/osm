#! /bin/sh

set -e

. ../config

$PREFIX psql "$DATABASE" << SQL
DROP TABLE IF EXISTS rivers_intersections;
CREATE TABLE rivers_intersections
AS
SELECT DISTINCT ON (rt.id, rtt2.id)
       rt.id AS id1,   rt.tags->'name' AS name1,  wg.id AS way1,
       rtt2.id AS id2, rtt2.tags->'name' AS name2, wg2.id AS way2
FROM relations rt
JOIN relation_members rm ON rm.relation_id = rt.id AND rm.member_type = 'W'
JOIN ways wg ON wg.id = rm.member_id AND ST_IsValid(wg.linestring) AND
                St_NPoints(wg.linestring) > 1

JOIN relations rtt2 ON rtt2.tags ? 'type' AND rtt2.tags->'type' = 'waterway' AND
                       rtt2.id > rt.id
JOIN relation_members rm2 ON rm2.relation_id = rtt2.id AND rm2.member_type = 'W'
JOIN ways wg2 ON wg2.id = rm2.member_id AND ST_IsValid(wg2.linestring) AND
                 St_NPoints(wg2.linestring) > 1 AND
                 (wg.bbox && wg2.bbox) AND
                 ST_Intersects(wg.linestring, wg2.linestring)

WHERE rt.tags ? 'type' AND rt.tags->'type' = 'waterway' AND
      wg.nodes[array_length(wg.nodes, 1)] != wg2.nodes[array_length(wg2.nodes, 1)];
ALTER TABLE rivers_intersections OWNER to osmosis;


DROP TABLE IF EXISTS rivers_coastline_intersections;
CREATE TABLE rivers_coastline_intersections
AS
SELECT DISTINCT ON (rt.id)
       rt.id AS id1, rt.tags->'name' AS name1,  wg.id AS way1,
       wg2.id AS way2
FROM relations rt
JOIN relation_members rm ON rm.relation_id = rt.id AND rm.member_type = 'W' AND
                            rm.member_role != 'waterbank'
JOIN ways wg ON wg.id = rm.member_id AND ST_IsValid(wg.linestring)

JOIN ways wg2 ON wg2.tags ? 'natural' AND wg2.tags->'natural' = 'coastline' AND
                 ST_IsValid(wg2.linestring) AND
                 (wg.bbox && wg2.bbox) AND
                 ST_Intersects(wg.linestring, wg2.linestring)

WHERE rt.tags ? 'type' AND rt.tags->'type' = 'waterway';
ALTER TABLE rivers_coastline_intersections OWNER to osmosis;

SQL

php suivi-affluents.php > suivi-affluents.html
