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

CREATE INDEX idx_nodes_tags_power ON nodes USING btree((tags->'power')) where tags ? 'power';

CREATE INDEX idx_ways_tags_admin_level ON ways USING btree((tags->'admin_level')) where tags ? 'admin_level';
CREATE INDEX idx_ways_tags_amenity ON ways USING btree((tags->'amenity')) where tags ? 'amenity';
CREATE INDEX idx_ways_tags_building ON ways USING btree((tags->'building')) where tags ? 'building';
CREATE INDEX idx_ways_tags_highway ON ways USING btree((tags->'highway')) where tags ? 'highway';
CREATE INDEX idx_ways_tags_landuse ON ways USING btree((tags->'landuse')) where tags ? 'landuse';
CREATE INDEX idx_ways_tags_leisure ON ways USING btree((tags->'leisure')) where tags ? 'leisure';
CREATE INDEX idx_ways_tags_natural ON ways USING btree((tags->'natural')) where tags ? 'natural';
CREATE INDEX idx_ways_tags_power ON ways USING btree((tags->'power')) where tags ? 'power';
CREATE INDEX idx_ways_tags_railway ON ways USING btree((tags->'railway')) where tags ? 'railway';
CREATE INDEX idx_ways_tags_waterway ON ways USING btree((tags->'waterway')) where tags ? 'waterway';

CREATE INDEX idx_relations_tags_type ON relations USING btree((tags->'type')) where tags ? 'type';
