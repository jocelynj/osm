#! /bin/sh

set -e

. ../config

psql "$DATABASE" << SQL
DROP TABLE osm_autoroutes;
CREATE TABLE osm_autoroutes
AS
SELECT rt.id AS relation_id, COUNT(w.id) AS num_way,
       (CASE WHEN rt.tags->'network' = 'FR:A-road' THEN rt.tags->'ref'
             WHEN rt.tags->'name' = 'Boulevard Périphérique de Paris' THEN 'BP'
        END) AS ref,
       rt.tags->'name' AS name,
       st_numgeometries(st_linemerge(st_union(st_transform(linestring,2154)))) AS num_sections,
       SUM(st_length(st_transform(linestring,2154))) / 1000 / 2 as km,
       SUM(st_length(st_transform((CASE WHEN w.tags->'oneway'='yes' THEN linestring ELSE NULL END),2154))) / 1000 as km_oneway_yes,
       SUM(st_length(st_transform((CASE WHEN w.tags->'oneway'='no' THEN linestring ELSE NULL END),2154))) / 1000 as km_oneway_no,
       SUM(st_length(st_transform((CASE WHEN NOT w.tags ? 'oneway' THEN linestring ELSE NULL END),2154))) / 1000 as km_oneway_null

FROM relations rt
JOIN relation_members ON rt.id = relation_members.relation_id AND
                         relation_members.member_type = 'W' AND
                         relation_members.member_role = ''
JOIN ways w ON relation_members.member_id = w.id

WHERE rt.tags->'type' = 'route' AND rt.tags->'route' = 'road' AND
      (rt.tags->'network' = 'FR:A-road' AND rt.tags ? 'ref' OR
       rt.tags->'name' = 'Boulevard Périphérique de Paris')
GROUP BY rt.id, rt.tags->'name', rt.tags->'network', rt.tags->'name', rt.tags->'ref';


DROP TABLE osm_autoroutes_sorties;
CREATE TABLE osm_autoroutes_sorties
AS
SELECT autoroutes.id,
       osm_autoroutes.relation_id, osm_autoroutes.ref AS relation_ref,
       nodes.tags->'ref' AS ref, nodes.tags->'name' AS name, nodes.tags->'exit_to' AS exit_to,
       concat(nodes.id) AS nodes_id,
       COUNT(*) AS total
FROM osm_autoroutes
JOIN autoroutes ON osm_autoroutes.ref = autoroutes.ref
JOIN relation_members ON osm_autoroutes.relation_id = relation_members.relation_id AND
                         relation_members.member_type = 'W' AND
                         relation_members.member_role = ''
JOIN way_nodes ON relation_members.member_id = way_nodes.way_id
JOIN nodes ON way_nodes.node_id = nodes.id
WHERE nodes.tags ? 'highway'
GROUP BY autoroutes.id, osm_autoroutes.relation_id, osm_autoroutes.ref,
          nodes.tags->'ref', nodes.tags->'name', nodes.tags->'exit_to';

DROP TABLE osm_autoroutes_aires;
CREATE TABLE osm_autoroutes_aires
AS
SELECT autoroutes.id,
       osm_autoroutes.relation_id, osm_autoroutes.ref AS relation_ref,
       nodes.tags->'name' AS name, nodes.id AS node_id,
       nodes.tags->'highway' AS highway,
       int4(MIN(ST_Distance(st_transform(nodes.geom,2154),
                            st_transform(linestring,2154)))) AS distance
FROM osm_autoroutes
JOIN autoroutes ON osm_autoroutes.ref = autoroutes.ref
JOIN relation_members ON osm_autoroutes.relation_id = relation_members.relation_id AND
                         relation_members.member_type = 'W' AND
                         relation_members.member_role = ''
JOIN ways ON ways.id = relation_members.member_id
JOIN nodes ON ST_Distance(st_transform(nodes.geom,2154),
                          st_transform(linestring,2154)) < 1000
WHERE nodes.tags->'highway' = 'services' OR nodes.tags->'highway' = 'rest_area'
GROUP BY autoroutes.id, osm_autoroutes.relation_id, osm_autoroutes.ref,
         nodes.id, nodes.tags->'name', nodes.tags->'highway';
SQL

php suivi-autoroutes.php > suivi-autoroutes.html
php suivi-autoroutes-sorties.php >  suivi-autoroutes-sorties.html
php suivi-autoroutes-aires.php >  suivi-autoroutes-aires.html
