-- Update the linestring column of the way table.
UPDATE ways w SET linestring = (
       SELECT MakeLine(c.geom) AS way_line FROM (
               SELECT n.geom AS geom
               FROM nodes n INNER JOIN way_nodes wn ON n.id = wn.node_id
               WHERE (wn.way_id = w.id) ORDER BY wn.sequence_id
       ) c
);
