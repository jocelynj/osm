-- Drop all primary keys and indexes to improve load speed.
ALTER TABLE nodes DROP CONSTRAINT pk_nodes;
ALTER TABLE ways DROP CONSTRAINT pk_ways;
ALTER TABLE way_nodes DROP CONSTRAINT pk_way_nodes;
ALTER TABLE relations DROP CONSTRAINT pk_relations;
ALTER TABLE users DROP CONSTRAINT pk_users;
DROP INDEX idx_node_tags_node_id;
DROP INDEX idx_way_tags_way_id;
DROP INDEX idx_way_nodes_way_id;
DROP INDEX idx_relation_tags_relation_id;
DROP INDEX idx_relation_members_relation_id;

-- truncate all tables
TRUNCATE nodes;
TRUNCATE node_tags;
TRUNCATE ways;
TRUNCATE way_tags;
TRUNCATE way_nodes;
TRUNCATE relations;
TRUNCATE relation_tags;
TRUNCATE relation_members;
TRUNCATE users;

-- Import the table data from the data files using the fast COPY method.
COPY nodes FROM '/home/jocelyn/gps/osm/france/change/pgimport/nodes.txt';
COPY node_tags FROM '/home/jocelyn/gps/osm/france/change/pgimport/node_tags.txt';
COPY ways FROM '/home/jocelyn/gps/osm/france/change/pgimport/ways.txt';
COPY way_tags FROM '/home/jocelyn/gps/osm/france/change/pgimport/way_tags.txt';
COPY way_nodes FROM '/home/jocelyn/gps/osm/france/change/pgimport/way_nodes.txt';
COPY relations FROM '/home/jocelyn/gps/osm/france/change/pgimport/relations.txt';
COPY relation_tags FROM '/home/jocelyn/gps/osm/france/change/pgimport/relation_tags.txt';
COPY relation_members FROM '/home/jocelyn/gps/osm/france/change/pgimport/relation_members.txt';
COPY users FROM '/home/jocelyn/gps/osm/france/change/pgimport/users.txt';

-- Add the primary keys and indexes back again (except the way bbox index).
ALTER TABLE ONLY nodes ADD CONSTRAINT pk_nodes PRIMARY KEY (id);
ALTER TABLE ONLY ways ADD CONSTRAINT pk_ways PRIMARY KEY (id);
ALTER TABLE ONLY way_nodes ADD CONSTRAINT pk_way_nodes PRIMARY KEY (way_id, sequence_id);
ALTER TABLE ONLY relations ADD CONSTRAINT pk_relations PRIMARY KEY (id);
ALTER TABLE ONLY users ADD CONSTRAINT pk_users PRIMARY KEY (id);
CREATE INDEX idx_node_tags_node_id ON node_tags USING btree (node_id);
CREATE INDEX idx_ways_id ON ways USING btree (id);
CREATE INDEX idx_way_tags_way_id ON way_tags USING btree (way_id);
CREATE INDEX idx_way_nodes_way_id ON way_nodes USING btree (way_id);
CREATE INDEX idx_relation_tags_relation_id ON relation_tags USING btree (relation_id);
CREATE INDEX idx_relation_members_relation_id ON relation_members USING btree (relation_id);

CREATE INDEX idx_relation_tags_k ON relation_tags USING btree (k);


-- Perform database maintenance due to large database changes.
VACUUM ANALYZE;
