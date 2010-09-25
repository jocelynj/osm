#! /bin/bash

PREFIX=/usr/bin/time
OSMOSIS="$PREFIX osmosis -q"

CHANGEFILE="change-`date +%F-%R`.osc.gz"

echo ""
echo "*** Get changes from server"
$OSMOSIS --read-replication-interval --simplify-change --write-xml-change $CHANGEFILE

echo ""
echo "*** Insert data in postgresql"
$OSMOSIS --read-xml-change $CHANGEFILE --write-pgsql-change password=osm

echo ""
echo "*** Update table way_geometry"
$PREFIX psql osm < UpdateGeometryForWays.sql
