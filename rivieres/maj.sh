#! /bin/sh

. ../config

$PREFIX psql "$DATABASE" << SQL
DROP TABLE rivers_intersections;
CREATE TABLE rivers_intersections
AS
SELECT DISTINCT ON (rt.relation_id, rtt2.relation_id)
       rt.relation_id AS id1,   rtn.v AS name1,  wg.way_id AS way1,
       rtt2.relation_id AS id2, rtn2.v AS name2, wg2.way_id AS way2
FROM relation_tags rt
LEFT JOIN relation_tags rtn ON rt.relation_id = rtn.relation_id AND rtn.k = 'name'
JOIN relation_members rm ON rm.relation_id = rt.relation_id AND rm.member_type = 'W'
JOIN way_geometry wg ON wg.way_id = rm.member_id
JOIN way_nodes wn1 ON wn1.way_id = wg.way_id AND
                      wn1.sequence_id = (SELECT MAX(sequence_id) FROM way_nodes
                                         WHERE way_nodes.way_id = wg.way_id)

JOIN relation_tags rtt2 ON rtt2.k = 'type' AND rtt2.v = 'waterway' AND
                           rtt2.relation_id > rt.relation_id
JOIN relation_members rm2 ON rm2.relation_id = rtt2.relation_id AND rm2.member_type = 'W'
JOIN way_geometry wg2 ON wg2.way_id = rm2.member_id AND ST_Intersects(wg.geom, wg2.geom)
LEFT JOIN relation_tags rtn2 ON rm2.relation_id = rtn2.relation_id AND rtn2.k = 'name'
JOIN way_nodes wn2 ON wn2.way_id = wg2.way_id AND
                      wn2.sequence_id = (SELECT MAX(sequence_id) FROM way_nodes
                                         WHERE way_nodes.way_id = wg2.way_id)

WHERE rt.k = 'type' AND rt.v = 'waterway' AND wn1.node_id != wn2.node_id;
ALTER TABLE rivers_intersections OWNER to osm;


DROP TABLE rivers_coastline_intersections;
CREATE TABLE rivers_coastline_intersections
AS
SELECT DISTINCT ON (rt.relation_id)
       rt.relation_id AS id1,   rtn.v AS name1,  wg.way_id AS way1,
       wg2.way_id AS way2
FROM relation_tags rt
LEFT JOIN relation_tags rtn ON rt.relation_id = rtn.relation_id AND rtn.k = 'name'
JOIN relation_members rm ON rm.relation_id = rt.relation_id AND rm.member_type = 'W' AND
                            rm.member_role != 'waterbank'
JOIN way_geometry wg ON wg.way_id = rm.member_id

JOIN way_tags wtn2 ON wtn2.k = 'natural' AND wtn2.v = 'coastline'
JOIN way_geometry wg2 ON wg2.way_id = wtn2.way_id AND ST_Intersects(wg.geom, wg2.geom)

WHERE rt.k = 'type' AND rt.v = 'waterway';
ALTER TABLE rivers_coastline_intersections OWNER to osm;

SQL

rm suivi-affluents.html
wget -O suivi-affluents.html http://jocelyn.dnsalias.org/~jocelyn/osm/suivi-affluents.php
cp suivi-affluents.html suivi-affluents.`grep "en date du ....-..-.." suivi-affluents.html |
                                         head -1 |
                                         sed "s/.*en date du \(....-..-..\).*/\1/"`.html

(cp suivi-affluents.html ~/online/site-alwaysdata-jocelyn/osm &&
 cd ~/online/site-alwaysdata-jocelyn &&
 ./update.sh)

