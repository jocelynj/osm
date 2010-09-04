------------------------------------------------------------------------------
-- Frédéric Rodrigo - 2010 : initial
-- Etienne Chové    - 2010 : ST_NumPoints(geom) >= 4
------------------------------------------------------------------------------

-- drop table if it exists
DROP TABLE IF EXISTS way_geometry;

-- create table
CREATE TABLE way_geometry (
  way_id bigint NOT NULL
);
ALTER TABLE way_geometry OWNER TO osm;

-- add PostGIS geometry column
SELECT AddGeometryColumn('', 'way_geometry', 'geom', 4326, 'GEOMETRY', 2);

INSERT INTO
	way_geometry
SELECT
	ways.id,
	(
		SELECT
			ST_LineFromMultiPoint(Collect(nodes.geom))
		FROM
			nodes
				JOIN way_nodes ON nodes.id = way_nodes.node_id
		WHERE
			ways.id = way_nodes.way_id
	)
FROM
	ways, relation_members, relation_tags
WHERE
	ways.id = member_id AND member_type = 'W' AND
        relation_members.relation_id = relation_tags.relation_id AND
        ((relation_tags.k = 'type' AND relation_tags.v = 'route') OR
         relation_tags.k = 'waterway')
GROUP BY ways.id
;

UPDATE
	way_geometry
SET
	geom = ST_MakePolygon(geom)
WHERE
	ST_IsClosed(geom) AND
	ST_NumPoints(geom) >= 4
;

DELETE FROM way_geometry WHERE ST_NPoints(geom) = 1;

CREATE UNIQUE INDEX idx_way_geometry_way_id ON way_geometry USING btree (way_id);
--CREATE INDEX idx_way_geometry_geom ON way_geometry USING gist (geom);
