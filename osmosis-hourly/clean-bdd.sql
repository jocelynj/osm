\set france_square '\'0103000020E610000001000000050000006E1A3625B41016C0416BD9B5188C44406E1A3625B41016C086B82869B4AA49406E7A617CE256244086B82869B4AA49406E7A617CE2562440416BD9B5188C44406E1A3625B41016C0416BD9B5188C4440\'::geometry'

DROP TABLE nodes_to_remove;
DROP TABLE ways_to_remove;
DROP TABLE relations_to_remove;
DROP TABLE relation_members_clean;

-- nodes
CREATE TABLE
nodes_to_remove
AS
SELECT id
FROM nodes
WHERE NOT ST_Contains(:france_square, geom);

DELETE
FROM nodes
USING nodes_to_remove
WHERE nodes.id = nodes_to_remove.id;

DELETE
FROM node_tags
USING nodes_to_remove
WHERE node_id = nodes_to_remove.id;

-- ways
DELETE
FROM way_nodes
USING nodes_to_remove
WHERE node_id = nodes_to_remove.id;

DELETE
FROM way_nodes
WHERE way_id IN (SELECT way_id
                  FROM way_nodes
                  LEFT JOIN nodes on nodes.id = way_nodes.node_id
                  WHERE nodes.id IS NULL
                 );

CREATE TABLE
ways_to_remove
AS
SELECT id
FROM ways
LEFT JOIN way_nodes ON way_id = id
WHERE way_id IS NULL;

DELETE
FROM ways
USING ways_to_remove
WHERE ways_to_remove.id = ways.id;

DELETE
FROM way_tags
USING ways_to_remove
WHERE ways_to_remove.id = way_tags.way_id;

-- relations
DELETE
FROM relation_members
USING nodes_to_remove
WHERE relation_members.member_type = 'N' AND relation_members.member_id = nodes_to_remove.id;

DELETE
FROM relation_members
USING ways_to_remove
WHERE relation_members.member_type = 'W' AND relation_members.member_id = ways_to_remove.id;

CREATE TABLE
relations_to_remove
AS
SELECT id
FROM relations
LEFT JOIN relation_members ON relation_id = id
WHERE relation_id IS NULL;

DELETE
FROM relations
USING relations_to_remove
WHERE relations_to_remove.id = relations.id;

DELETE
FROM relation_tags
USING relations_to_remove
WHERE relations_to_remove.id = relation_tags.relation_id;



-- check
CREATE TABLE
relation_members_clean
AS
SELECT relation_members.relation_id, relation_members.member_id, relation_members.member_type
FROM relation_members
LEFT JOIN nodes ON relation_members.member_type = 'N' AND relation_members.member_id = nodes.id
LEFT JOIN ways ON relation_members.member_type = 'W' AND relation_members.member_id = ways.id
LEFT JOIN relations ON relation_members.member_type = 'R' AND relation_members.member_id = relations.id
WHERE nodes.id IS NULL AND ways.id IS NULL AND relations.id IS NULL;

DELETE
FROM relation_members
USING relation_members_clean
WHERE relation_members_clean.relation_id = relation_members.relation_id AND
      relation_members_clean.member_id   = relation_members.member_id AND
      relation_members_clean.member_type = relation_members.member_type;
