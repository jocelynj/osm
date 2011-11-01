DROP FUNCTION update_bounding_box(bbox_name text, rel_id integer);

CREATE OR REPLACE FUNCTION update_bounding_box(bbox_name text, rel_id integer) RETURNS integer
AS $BODY$
BEGIN
  DELETE FROM bounding_box WHERE name = bbox_name;

  INSERT INTO bounding_box
  VALUES (bbox_name,
  (
  SELECT ST_Union(a.geom)
  FROM (
    SELECT st_makepolygon(St_exteriorring(ST_Buffer((ST_Dump(p_geom)).geom, 0.02,
                                                    'quad_segs=1'))) AS geom
    FROM (
      SELECT st_Polygonize(ST_LineMerge(w.linestring)) AS p_geom
      FROM relations r
      LEFT JOIN relation_members rm ON rm.relation_id = r.id AND rm.member_type != 'N' AND
                                       rm.member_role != 'exclave'
      LEFT JOIN relation_members rm2 ON rm2.relation_id = rm.member_id AND rm.member_type = 'R' AND
                                        rm2.member_type != 'N' AND rm2.member_role != 'exclave'
      LEFT JOIN relation_members rm3 ON rm3.relation_id = rm2.member_id AND rm2.member_type = 'R' AND
                                        rm3.member_type != 'N' AND rm3.member_role != 'exclave'
      LEFT JOIN relation_members rm4 ON rm4.relation_id = rm3.member_id AND rm3.member_type = 'R' AND
                                        rm4.member_type != 'N' AND rm4.member_role != 'exclave'
      LEFT JOIN relation_members rm5 ON rm5.relation_id = rm4.member_id AND rm4.member_type = 'R' AND
                                        rm5.member_type != 'N' AND rm5.member_role != 'exclave'
      LEFT JOIN relation_members rm6 ON rm6.relation_id = rm5.member_id AND rm5.member_type = 'R' AND
                                        rm6.member_type != 'N' AND rm6.member_role != 'exclave'
      LEFT JOIN ways w ON (w.id = rm.member_id AND rm.member_type = 'W') OR
                          (w.id = rm2.member_id AND rm2.member_type = 'W') OR
                          (w.id = rm3.member_id AND rm3.member_type = 'W') OR
                          (w.id = rm4.member_id AND rm4.member_type = 'W') OR
                          (w.id = rm5.member_id AND rm5.member_type = 'W') OR
                          (w.id = rm6.member_id AND rm6.member_type = 'W')
      WHERE r.id = rel_id AND w.linestring IS NOT NULL
    ) AS b
  ) AS a
  ));
  RETURN st_npoints(geom) FROM bounding_box WHERE name = bbox_name;
END
$BODY$
LANGUAGE 'plpgsql' ;

