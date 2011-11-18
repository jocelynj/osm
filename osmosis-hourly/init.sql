CREATE OR REPLACE FUNCTION way_geom(way_id bigint) RETURNS geometry AS
$BODY$
  SELECT linestring
  FROM ways
  WHERE id = $1;
$BODY$
LANGUAGE 'SQL' ;

