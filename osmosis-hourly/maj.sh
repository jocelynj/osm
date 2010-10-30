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
echo "*** Clean database"
$PREFIX psql "$DATABASE" < clean-bdd.sql

echo ""
echo "*** Update table way_geometry"
$PREFIX psql "$DATABASE" < UpdateGeometryForWays.sql

