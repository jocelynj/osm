#! /bin/sh

for t in nodes ways relations; do
  echo $t
  for i in `psql -t -q -c "SELECT ci.relname from pg_index i,pg_class ci,pg_class ct where i.indexrelid=ci.oid and i.indrelid=ct.oid and ct.relname='$t'" osm`;do
    psql -c "drop index $i" osm;
  done
done

for t in nodes ways relations way_nodes relation_members users; do
  psql -c "TRUNCATE $t" osm
done
