#! /bin/sh

. ../config

$PREFIX psql "$DATABASE" << SQL
DROP TABLE rivers_intersections;
CREATE TABLE rivers_intersections
AS
SELECT DISTINCT ON (rt.id, rtt2.id)
       rt.id AS id1,   rt.tags->'name' AS name1,  wg.id AS way1,
       rtt2.id AS id2, rtt2.tags->'name' AS name2, wg2.id AS way2
FROM relations rt
JOIN relation_members rm ON rm.relation_id = rt.id AND rm.member_type = 'W'
JOIN ways wg ON wg.id = rm.member_id
JOIN way_nodes wn1 ON wn1.way_id = wg.id AND
                      wn1.sequence_id = (SELECT MAX(sequence_id) FROM way_nodes
                                         WHERE way_nodes.way_id = wg.id)

JOIN relations rtt2 ON rtt2.tags->'type' = 'waterway' AND
                       rtt2.id > rt.id
JOIN relation_members rm2 ON rm2.relation_id = rtt2.id AND rm2.member_type = 'W'
JOIN ways wg2 ON wg2.id = rm2.member_id AND (wg.bbox && wg2.bbox) AND
                 ST_Intersects(wg.linestring, wg2.linestring)
JOIN way_nodes wn2 ON wn2.way_id = wg2.id AND
                      wn2.sequence_id = (SELECT MAX(sequence_id) FROM way_nodes
                                         WHERE way_nodes.way_id = wg2.id)

WHERE rt.tags->'type' = 'waterway' AND wn1.node_id != wn2.node_id;
ALTER TABLE rivers_intersections OWNER to osmosis;


DROP TABLE rivers_coastline_intersections;
CREATE TABLE rivers_coastline_intersections
AS
SELECT DISTINCT ON (rt.id)
       rt.id AS id1,   rt.tags->'name' AS name1,  wg.id AS way1,
       wg2.id AS way2
FROM relations rt
JOIN relation_members rm ON rm.relation_id = rt.id AND rm.member_type = 'W' AND
                            rm.member_role != 'waterbank'
JOIN ways wg ON wg.id = rm.member_id

JOIN ways wg2 ON wg2.tags->'natural' = 'coastline' AND (wg.bbox && wg2.bbox) AND
                 ST_Intersects(wg.linestring, wg2.linestring)

WHERE rt.tags->'type' = 'waterway';
ALTER TABLE rivers_coastline_intersections OWNER to osmosis;

SQL

php suivi-affluents.php > suivi-affluents.html
