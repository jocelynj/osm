#! /bin/sh

set -e

. ../config

$PREFIX psql "$DATABASE" << SQL
DROP TABLE IF EXISTS rivers_intersections;
CREATE TABLE rivers_intersections
AS
SELECT
    r1.id AS id1, r1.tags->'name' AS name1, wn1.way_id AS way1,
    r2.id AS id2, r2.tags->'name' AS name2, wn2.way_id AS way2
FROM
    relations AS r1
    JOIN relation_members AS rm1 ON
        r1.id = rm1.relation_id AND
        rm1.member_type = 'W'
    JOIN way_nodes AS wn1 ON
        rm1.member_id = wn1.way_id
    JOIN way_nodes AS wn2 ON
        wn1.way_id != wn2.way_id AND
        wn1.node_id = wn2.node_id
    JOIN relation_members AS rm2 ON
        wn2.way_id = rm2.member_id AND
        rm2.member_type = 'W' AND
        rm2.relation_id > rm1.relation_id
    JOIN relations AS r2 ON
        rm2.relation_id = r2.id
WHERE
    r1.tags?'type' AND
    r1.tags->'type' = 'waterway' AND
    r2.tags?'type' AND
    r2.tags->'type' = 'waterway';
ALTER TABLE rivers_intersections OWNER to osmosis;
SQL

$PREFIX psql "$DATABASE" << SQL
DROP TABLE IF EXISTS rivers_coastline_intersections;
CREATE TABLE rivers_coastline_intersections
AS
SELECT DISTINCT ON (rt.id)
       rt.id AS id1, rt.tags->'name' AS name1, wn1.way_id AS way1,
       wg2.id AS way2
FROM relations rt
JOIN relation_members rm ON rm.relation_id = rt.id AND rm.member_type = 'W' AND
                            rm.member_role != 'waterbank'
JOIN way_nodes AS wn1 ON rm.member_id = wn1.way_id
JOIN way_nodes AS wn2 ON wn1.way_id != wn2.way_id AND
                         wn1.node_id = wn2.node_id
 
JOIN ways wg2 ON wg2.tags ? 'natural' AND wg2.tags->'natural' = 'coastline' AND
                 wg2.id = wn2.way_id

WHERE rt.tags ? 'type' AND rt.tags->'type' = 'waterway';
ALTER TABLE rivers_coastline_intersections OWNER to osmosis;

SQL

$PREFIX php suivi-affluents.php > suivi-affluents.html
