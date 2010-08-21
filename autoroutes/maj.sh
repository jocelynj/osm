#! /bin/sh

psql osm << SQL
DROP TABLE osm_autoroutes;
CREATE TABLE osm_autoroutes
AS
SELECT rt1.relation_id AS relation_id, COUNT(way_id) AS num_way,
       rt2.v AS ref, rtn.v AS name,
       st_numgeometries(st_linemerge(st_union(st_transform(geom,2154)))) AS num_sections,
       SUM(st_length(st_transform(geom,2154))) / 1000 / 2 as km
FROM relation_tags rt1
JOIN relation_tags rt2 ON rt1.relation_id = rt2.relation_id AND rt2.k='ref'
JOIN relation_tags rtt ON rt1.relation_id = rtt.relation_id AND rtt.k='type' AND
                                                                rtt.v='route'
JOIN relation_tags rtr ON rt1.relation_id = rtr.relation_id AND rtr.k='route' AND
                                                                rtr.v='road'
JOIN relation_members ON rt1.relation_id = relation_members.relation_id AND
                         relation_members.member_type = 'W'
JOIN way_geometry ON relation_members.member_id = way_geometry.way_id
LEFT JOIN relation_tags rtn ON rt1.relation_id = rtn.relation_id AND rtn.k='name'
WHERE rt1.k='network' AND rt1.v='FR:A-road'
GROUP BY rt1.relation_id, rt2.v, rtn.v;

ALTER TABLE osm_autoroutes OWNER TO osm;

SQL

rm suivi-autoroutes.html
wget -O suivi-autoroutes.html http://jocelyn.dnsalias.org/~jocelyn/osm/suivi-autoroutes.php
cp suivi-autoroutes.html suivi-autoroutes.`grep "en date du ....-..-.." suivi-autoroutes.html | sed "s/.*en date du \(....-..-..\).*/\1/"`.html
