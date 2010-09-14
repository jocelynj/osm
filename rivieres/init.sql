DROP VIEW rivers_tributary;
CREATE VIEW rivers_tributary 
AS
WITH RECURSIVE search_river(id, member_id, member_type, rivers, depth, path, cycle) AS (
        SELECT r.relation_id, r.member_id, r.member_type,
               ARRAY[ARRAY[100, r.relation_id, ascii('R')],
                     ARRAY[r.sequence_id, r.member_id, ascii(r.member_type)]],
               1,
               ARRAY[r.relation_id] || r.member_id,
               false
        FROM relation_members r
--        JOIN relation_tags rtr ON r.relation_id = rtr.relation_id AND rtr.k = 'ref:sandre'
        WHERE r.member_role = 'tributary'
      UNION ALL
        SELECT r.relation_id, r.member_id, r.member_type,
               sg.rivers ||
               ARRAY[r.sequence_id, r.member_id, ascii(r.member_type)],
               sg.depth + 1,
               path || r.member_id,
               r.member_id = ANY(path)
        FROM relation_members r
        JOIN search_river sg ON sg.member_type = 'R' AND r.relation_id = sg.member_id
        WHERE NOT cycle AND
              r.member_role = 'tributary'
)
SELECT DISTINCT ON (member_id, member_type) rivers, depth FROM search_river
ORDER BY member_id, member_type, depth DESC;
ALTER VIEW rivers_tributary OWNER TO osm;
