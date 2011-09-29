CREATE OR REPLACE FUNCTION delete(arr bigint[], val bigint) RETURNS bigint[] AS $$
BEGIN
  RETURN ARRAY (
    SELECT * FROM (SELECT UNNEST(arr) AS a) AS b WHERE a != val
  );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_way(deleted_way_id bigint) RETURNS void AS $$
BEGIN
  DELETE FROM relation_members WHERE member_type = 'W' AND member_id = deleted_way_id;
  DELETE FROM ways WHERE id = deleted_way_id;
  DELETE FROM nodes USING way_nodes WHERE nodes.id = way_nodes.node_id AND
                                          way_nodes.way_id = deleted_way_id;
  DELETE FROM way_nodes WHERE way_nodes.way_id = deleted_way_id;

  DELETE from actions WHERE data_type = 'W' AND id = deleted_way_id AND action != 'D';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION osmosisUpdate_way() RETURNS void AS $$
DECLARE
  line RECORD;
BEGIN
  FOR line IN SELECT actions.id AS id
              FROM actions
              JOIN ways ON ways.id = actions.id AND
                           ways.linestring IS NULL
              WHERE data_type = 'W' AND action != 'D'
  LOOP
--    RAISE NOTICE 'way1 - %', line.id;
    PERFORM delete_way(line.id);
  END LOOP;

  FOR line IN SELECT actions.id AS id
              FROM actions
              JOIN ways ON ways.id = actions.id AND st_npoints(ways.linestring) = 1
              JOIN bounding_box ON bounding_box.name = 'all' AND
                                   ST_Disjoint(ST_StartPoint(ways.linestring),
                                               bounding_box.geom)
              WHERE data_type = 'W' AND action != 'D'
  LOOP
--    RAISE NOTICE 'way2 - %', line.id;
    PERFORM delete_way(line.id);
  END LOOP;

  FOR line IN SELECT actions.id AS id
              FROM actions
              JOIN ways ON ways.id = actions.id AND st_npoints(ways.linestring) > 1
              JOIN bounding_box ON bounding_box.name = 'all' AND
                                   ST_Disjoint(ways.linestring, bounding_box.geom)
              WHERE data_type = 'W' AND action != 'D'
  LOOP
    RAISE NOTICE 'way3 - %', line.id;
    PERFORM delete_way(line.id);
  END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_node(deleted_node_id bigint) RETURNS void AS $$
BEGIN
  DELETE FROM relation_members WHERE member_type = 'N' AND member_id = deleted_node_id;
  DELETE FROM nodes WHERE id = deleted_node_id;

  DELETE from actions WHERE data_type = 'N' AND id = deleted_node_id AND action != 'D';
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION osmosisUpdate_node() RETURNS void AS $$
DECLARE
  line RECORD;
  way_node RECORD;
  nodes_list bigint[];
BEGIN
  FOR line IN SELECT actions.id AS id
              FROM actions
              LEFT JOIN nodes ON nodes.id = actions.id
              WHERE data_type = 'N' AND action != 'D' AND
                    nodes.id IS NULL
  LOOP
    RAISE NOTICE 'node1 - %', line.id;
    PERFORM delete_node(line.id);
  END LOOP;

  FOR line IN SELECT actions.id AS id
              FROM actions
              JOIN nodes ON nodes.id = actions.id
              JOIN bounding_box ON bounding_box.name = 'all' AND
                                   ST_Disjoint(nodes.geom, bounding_box.geom)
              LEFT JOIN way_nodes ON way_nodes.node_id = nodes.id
              WHERE data_type = 'N' AND action != 'D' AND
                    way_nodes.way_id IS NULL
  LOOP
    RAISE NOTICE 'node2 - %', line.id;
    PERFORM delete_node(line.id);
  END LOOP;
END;
$$ LANGUAGE plpgsql;


  FOR line IN SELECT actions.id AS id
              FROM actions
              JOIN nodes ON nodes.id = actions.id
              JOIN bounding_box ON bounding_box.name = 'all' AND
                                   ST_Disjoint(nodes.geom, bounding_box.geom)
              LEFT JOIN way_nodes ON way_nodes.node_id = nodes.id
              WHERE data_type = 'N' AND action != 'D' AND
                    way_nodes.way_id IS NULL
  LOOP
    RAISE NOTICE 'node2 - %', line.id;
    PERFORM delete_node(line.id);
  END LOOP


    DELETE FROM relation_members WHERE member_type = 'N' AND member_id = line.id;   
    FOR way_node IN SELECT * FROM way_nodes WHERE node_id = line.id LOOP
      SELECT delete(nodes, line.id) INTO nodes_list FROM ways WHERE ways.id = way_node.way_id;
      IF nodes_list IS NULL THEN
        DELETE FROM ways WHERE id = way_node.way_id;
      ELSE
        UPDATE ways SET nodes = nodes_list WHERE id = way_node.way_id;
      END IF;
    END LOOP;
    DELETE FROM way_nodes WHERE node_id = line.id;

    DELETE FROM nodes WHERE id = line.id;
    DELETE from actions WHERE data_type = 'N' AND id = line.id AND action != 'D';
  END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION osmosisUpdate() RETURNS void AS $$
DECLARE
BEGIN
  DROP TABLE IF EXISTS actions_bak;
  CREATE TABLE actions_bak AS SELECT * FROM actions;

END;
$$ LANGUAGE plpgsql;



-- exécution après osmosis

insert into actions select * from actions_bak;

SELECT * FROM osmosisUpdate_way();
SELECT * FROM osmosisUpdate_node();

