-- Update the bbox column of the way table.
UPDATE ways SET bbox = (
       SELECT Envelope(Collect(geom))
       FROM nodes JOIN way_nodes ON way_nodes.node_id = nodes.id
       WHERE way_nodes.way_id = ways.id
);
