#! /bin/bash

set -e

. ../config

CURDATE="`date +%F-%R`"

LOCKFILE="$WORKDIR/lock-osmosis-maj"
CHANGEFILE="$WORKDIR/change-${CURDATE}.osc.gz"
SOURCE_OSM_FILE="$WORKDIR/france.osm.pbf"
TARGET_OSM_FILE="$WORKDIR/france-${CURDATE}.osm.pbf"
POLYGON="$WORKDIR/france.poly"

if [ -e "$LOCKFILE" ]; then
  echo "Lock file $LOCKFILE still present - aborting update"
  exit 1
fi

touch $LOCKFILE

echo ""
echo "*** Get changes from server"
$OSMOSIS --read-replication-interval workingDirectory="$WORKDIR" --simplify-change --write-xml-change "$CHANGEFILE"

echo ""
echo "*** Update $SOURCE_OSM_FILE"
cd $WORKDIR
$OSMOSIS --read-xml-change "$CHANGEFILE" --read-pbf "$SOURCE_OSM_FILE" --apply-change --buffer --bounding-polygon file="$POLYGON" --write-pbf file="$TARGET_OSM_FILE"
rm "$SOURCE_OSM_FILE"
ln "$TARGET_OSM_FILE" "$SOURCE_OSM_FILE"

echo ""
echo "*** Insert data in postgresql"
$OSMOSIS --read-xml-change "$CHANGEFILE" --write-pgsql-change database="$DATABASE" user="$USER" password="$PASS"

echo ""
echo "*** Clean database"
$PREFIX psql "$DATABASE" -c "insert into actions select * from actions_bak;"
$PREFIX psql "$DATABASE" -c "SELECT * FROM osmosisUpdate_way1();"
$PREFIX psql "$DATABASE" -c "SELECT * FROM osmosisUpdate_way2();"
$PREFIX psql "$DATABASE" -c "SELECT * FROM osmosisUpdate_way3();"
$PREFIX psql "$DATABASE" -c "SELECT * FROM osmosisUpdate_node();"
$PREFIX psql "$DATABASE" -c "truncate actions;"

exit

echo ""
echo "*** Clean ways database"
$PREFIX psql "$DATABASE" -c "SELECT clean_bdd_ways_simple('$BOUNDING_BOX', 1000000, 1);"
$PREFIX psql "$DATABASE" -c "SELECT clean_bdd_ways_simple('$BOUNDING_BOX', 1000000, 2);"
$PREFIX psql "$DATABASE" -c "SELECT clean_bdd_ways_simple('$BOUNDING_BOX', 1000000, 10);"
$PREFIX psql "$DATABASE" -c "SELECT clean_bdd_ways('$BOUNDING_BOX', 1000000);"

if [ `date +%u` != 2 ]; then
  rm $LOCKFILE
  exit
fi

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
$PREFIX psql "$DATABASE" -c "CLUSTER way_nodes USING pk_way_nodes;"

echo ""
echo "*** ANALYZE"
$PREFIX psql "$DATABASE" -c "ANALYZE;"

rm $LOCKFILE
