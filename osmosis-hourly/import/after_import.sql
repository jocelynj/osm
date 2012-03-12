CREATE OR REPLACE FUNCTION way_geom(way_id bigint) RETURNS geometry AS
$BODY$
  SELECT linestring
  FROM ways
  WHERE id = $1;
$BODY$
LANGUAGE 'SQL' ;

--INSERT INTO bounding_box VALUES
--  ('all', (SELECT ST_Union(geom)
--           FROM bounding_box
--           WHERE name != 'all'));

CREATE INDEX idx_nodes_tags_addr_housenumber ON nodes USING btree((tags->'addr:housenumber')) where tags ? 'addr:housenumber';
CREATE INDEX idx_nodes_tags_amenity ON nodes USING btree((tags->'amenity')) where tags ? 'amenity';
CREATE INDEX idx_nodes_tags_description ON nodes USING btree((tags->'description')) where tags ? 'description';
CREATE INDEX idx_nodes_tags_heritage ON nodes USING btree((tags->'heritage')) where tags ? 'heritage';
CREATE INDEX idx_nodes_tags_leisure ON nodes USING btree((tags->'leisure')) where tags ? 'leisure';
CREATE INDEX idx_nodes_tags_man_made ON nodes USING btree((tags->'man_made')) where tags ? 'man_made';
CREATE INDEX idx_nodes_tags_power ON nodes USING btree((tags->'power')) where tags ? 'power';
CREATE INDEX idx_nodes_tags_shop ON nodes USING btree((tags->'shop')) where tags ? 'shop';
CREATE INDEX idx_nodes_tags_tourism ON nodes USING btree((tags->'tourism')) where tags ? 'tourism';

CREATE INDEX idx_ways_tags_addr_housenumber ON ways USING btree((tags->'addr:housenumber')) where tags ? 'addr:housenumber';
CREATE INDEX idx_ways_tags_admin_level ON ways USING btree((tags->'admin_level')) where tags ? 'admin_level';
CREATE INDEX idx_ways_tags_amenity ON ways USING btree((tags->'amenity')) where tags ? 'amenity';
CREATE INDEX idx_ways_tags_building ON ways USING btree((tags->'building')) where tags ? 'building';
CREATE INDEX idx_ways_tags_heritage ON ways USING btree((tags->'heritage')) where tags ? 'heritage';
CREATE INDEX idx_ways_tags_highway ON ways USING btree((tags->'highway')) where tags ? 'highway';
CREATE INDEX idx_ways_tags_highway_link ON ways USING btree((tags->'highway')) where tags ? 'highway' AND tags->'highway' LIKE '%_link';
CREATE INDEX idx_ways_tags_junction ON ways USING btree((tags->'junction')) where tags ? 'junction';
CREATE INDEX idx_ways_tags_landuse ON ways USING btree((tags->'landuse')) where tags ? 'landuse';
CREATE INDEX idx_ways_tags_leisure ON ways USING btree((tags->'leisure')) where tags ? 'leisure';
CREATE INDEX idx_ways_tags_natural ON ways USING btree((tags->'natural')) where tags ? 'natural';
CREATE INDEX idx_ways_tags_power ON ways USING btree((tags->'power')) where tags ? 'power';
CREATE INDEX idx_ways_tags_railway ON ways USING btree((tags->'railway')) where tags ? 'railway';
CREATE INDEX idx_ways_tags_shop ON ways USING btree((tags->'shop')) where tags ? 'shop';
CREATE INDEX idx_ways_tags_tourism ON ways USING btree((tags->'tourism')) where tags ? 'tourism';
CREATE INDEX idx_ways_tags_waterway ON ways USING btree((tags->'waterway')) where tags ? 'waterway';

CREATE INDEX idx_relations_tags_type ON relations USING btree((tags->'type')) where tags ? 'type';


CREATE OR REPLACE FUNCTION ways_is_polygon(nodes bigint[], linestring geometry, tags hstore)
RETURNS BOOLEAN
AS $$
BEGIN
  RETURN (array_length(nodes,1) > 3 AND
          nodes[array_lower(nodes,1)] = nodes[array_upper(nodes,1)] AND
          ST_NumPoints(linestring) > 3 AND ST_IsClosed(linestring) AND
          ST_IsValid(linestring) AND ST_IsSimple(linestring) AND
          ST_IsValid(ST_MakePolygon(linestring)) AND
          NOT (tags ? 'attraction' AND tags->'attraction' = 'roller_coaster'));
END
$$ LANGUAGE plpgsql;


ALTER TABLE ways ADD COLUMN is_polygon boolean;
UPDATE ways SET is_polygon = ways_is_polygon(nodes, linestring, tags);

--This function will be triggered after way update
CREATE OR REPLACE FUNCTION osmosis_ways_update_polygon() RETURNS trigger
AS $$
BEGIN
  IF NEW.linestring IS NOT NULL THEN
    NEW.is_polygon = ways_is_polygon(NEW.nodes, NEW.linestring, NEW.tags);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER osmosis_ways_insert ON ways;
DROP TRIGGER osmosis_ways_update ON ways;

CREATE TRIGGER osmosis_ways_insert BEFORE INSERT ON ways
     FOR EACH ROW EXECUTE PROCEDURE osmosis_ways_update_polygon();

CREATE TRIGGER osmosis_ways_update BEFORE UPDATE ON ways
     FOR EACH ROW EXECUTE PROCEDURE osmosis_ways_update_polygon();

CREATE OR REPLACE FUNCTION osmosisUpdate() RETURNS void AS $$
DECLARE
BEGIN
  DROP TABLE IF EXISTS actions_bak;
  CREATE TABLE actions_bak AS SELECT * FROM actions;

END;
$$ LANGUAGE plpgsql;

