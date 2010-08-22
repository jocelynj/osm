#! /bin/sh

set -e

A="$1"

echo "COPY (select node_id from way_tags t1 join way_tags t2 on t1.way_id = t2.way_id and t2.k='highway' and t2.v='motorway' join way_nodes on way_nodes.way_id = t1.way_id where t1.v='$A') TO '/tmp/$A-nodes'" | psql -q osm;

echo "COPY (select t1.way_id from way_tags t1 join way_tags t2 on t1.way_id = t2.way_id and t2.k='highway' and t2.v='motorway' where t1.v='$A') TO '/tmp/$A-way'" | psql -q osm;

cat "/tmp/$A-nodes" | ../get-josm-node-bulk.py
cat "/tmp/$A-way" | ../get-josm-way-bulk.py
