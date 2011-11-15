CREATE OR REPLACE FUNCTION ends(linestring geometry) RETURNS SETOF geometry AS $$
DECLARE BEGIN
    RETURN NEXT ST_PointN(linestring,1);
    RETURN NEXT ST_PointN(linestring,ST_NPoints(linestring));
    RETURN;
END
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION update_bounding_box(bbox_name text, rel_id integer) RETURNS integer
AS $BODY$
DECLARE
  line RECORD;
  ok boolean;
BEGIN
  DELETE FROM bounding_box WHERE name = bbox_name;

  -- recup des way des relations
  CREATE TEMP TABLE tmp_way_poly AS
  WITH RECURSIVE deep_relation(id) AS (
        SELECT
            rel_id::bigint AS member_id
    UNION
        SELECT
            relation_members.member_id
        FROM
            deep_relation
            JOIN relation_members ON
                relation_members.relation_id = deep_relation.id AND
                relation_members.member_type = 'R'
  )
  SELECT
    ways.linestring
  FROM
    deep_relation
    JOIN relation_members ON
        relation_members.relation_id = deep_relation.id AND
        relation_members.member_type = 'W'
    JOIN ways ON
        ways.id = relation_members.member_id
  ;

  SELECT INTO ok 't';

  FOR line in SELECT
             ST_X(geom) AS x, ST_Y(geom) AS y
           FROM
             (SELECT ends(linestring) AS geom FROM tmp_way_poly) AS d
           GROUP BY
             geom
           HAVING
             COUNT(*) != 2
  LOOP
    SELECT INTO ok 'f';
    RAISE NOTICE 'missing - %f %f', line.x, line.y;
  END LOOP;

  INSERT INTO bounding_box
  VALUES (bbox_name,
          (select st_collect(ST_Buffer(st_makepolygon(geom), 0.02, 'quad_segs=1')) from (select (st_dump(st_linemerge(st_collect(linestring)))).geom from tmp_way_poly) as d
         ));

  RETURN st_npoints(geom) FROM bounding_box WHERE name = bbox_name;
END
$BODY$
LANGUAGE 'plpgsql' ;
