------------------------------------------------------------------------------
-- Frédéric Rodrigo - 2010 : initial
-- Etienne Chové    - 2010 : ST_NumPoints(geom) >= 4
------------------------------------------------------------------------------

DELETE FROM
	way_geometry
USING
	ways
WHERE
	ways.id = way_geometry.way_id AND ways.version <> way_geometry.version;

DELETE FROM
	way_geometry
WHERE
	way_id IN (SELECT way_id FROM way_geometry
                   LEFT JOIN ways ON way_geometry.way_id = ways.id
	           WHERE ways.id IS NULL)
;


INSERT INTO
	way_geometry
SELECT
	ways.id,
        ways.version,
	(
		SELECT
			ST_LineFromMultiPoint(Collect(nodes.geom))
		FROM
			way_nodes
		JOIN
			nodes ON nodes.id = way_nodes.node_id
		WHERE
			ways.id = way_nodes.way_id
	)
FROM
	ways
JOIN
	way_nodes ON way_nodes.way_id = ways.id AND sequence_id = 2
LEFT JOIN
	way_geometry ON ways.id = way_geometry.way_id
WHERE
	way_geometry.way_id IS NULL;

UPDATE
	way_geometry
SET
	geom = ST_MakePolygon(geom)
WHERE
	ST_IsClosed(geom) AND
	ST_NumPoints(geom) >= 4
;

DELETE FROM way_geometry WHERE ST_NPoints(geom) = 1;
