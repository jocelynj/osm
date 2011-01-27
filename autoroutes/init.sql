CREATE TABLE autoroutes (id integer, ref text, longueur float);
CREATE INDEX autoroutes_id ON autoroutes USING btree(id);

CREATE FUNCTION concat(text, bigint) RETURNS text AS $$
    SELECT $1 || '-' || text($2);
$$ LANGUAGE SQL;


CREATE AGGREGATE concat (
    sfunc = concat,
    basetype = bigint,
    stype = text,
    initcond = '0'
);


