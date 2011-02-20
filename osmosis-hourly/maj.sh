#! /bin/bash

. ../config

CHANGEFILE="$WORKDIR/change-`date +%F-%R`.osc.gz"

echo ""
echo "*** Get changes from server"
$OSMOSIS --read-replication-interval workingDirectory="$WORKDIR" --simplify-change --write-xml-change "$CHANGEFILE"

echo ""
echo "*** Insert data in postgresql"
$OSMOSIS --read-xml-change "$CHANGEFILE" --write-pgsql-change database="$DATABASE" user="$USER" password="$PASS"

echo ""
echo "*** Clean ways database"
$PREFIX psql "$DATABASE" -c "SELECT clean_bdd_ways_simple('$BOUNDING_BOX', 1000000, 1);"
$PREFIX psql "$DATABASE" -c "SELECT clean_bdd_ways_simple('$BOUNDING_BOX', 1000000, 2);"
$PREFIX psql "$DATABASE" -c "SELECT clean_bdd_ways_simple('$BOUNDING_BOX', 1000000, 10);"
$PREFIX psql "$DATABASE" -c "SELECT clean_bdd_ways('$BOUNDING_BOX', 1000000);"

echo ""
echo "*** Clean nodes database"
$PREFIX psql "$DATABASE" -c "SELECT clean_bdd_nodes('$BOUNDING_BOX', 1000000);"

echo ""
echo "*** CLUSTER nodes"
$PREFIX psql "$DATABASE" -c "CLUSTER nodes USING pk_nodes;"

echo ""
echo "*** CLUSTER ways"
$PREFIX psql "$DATABASE" -c "CLUSTER ways USING idx_ways_bbox;"

echo ""
echo "*** CLUSTER ways_nodes"
$PREFIX psql "$DATABASE" -c "CLUSTER way_nodes USING idx_way_nodes_way_id;"

echo ""
echo "*** VACUUM"
$PREFIX psql "$DATABASE" -c "VACUUM ANALYZE;"
