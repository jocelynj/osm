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

#echo ""
#echo "*** Update $SOURCE_OSM_FILE"
#cd $WORKDIR
#$OSMOSIS --read-xml-change "$CHANGEFILE" --read-pbf "$SOURCE_OSM_FILE" --apply-change --buffer --bounding-polygon file="$POLYGON" --write-pbf file="$TARGET_OSM_FILE"
#rm "$SOURCE_OSM_FILE"
#ln "$TARGET_OSM_FILE" "$SOURCE_OSM_FILE"

echo ""
echo "*** Insert data in postgresql"
$OSMOSIS --read-xml-change "$CHANGEFILE" --write-pgsql-change database="$DATABASE" user="$USER" password="$PASS"

echo ""
echo "*** Clean database"
$PREFIX psql "$DATABASE" -c "INSERT INTO actions SELECT * FROM actions_bak;"
$PREFIX psql "$DATABASE" -c "DELETE FROM actions WHERE action = 'D'"
$PREFIX psql "$DATABASE" -c "ANALYZE actions;"

$PREFIX psql "$DATABASE" -c "SELECT osmosisUpdate_way();"
$PREFIX psql "$DATABASE" -c "SELECT osmosisUpdate_node();"
$PREFIX psql "$DATABASE" -c "TRUNCATE actions;"

if [ `date +%u` != 2 ]; then
  rm $LOCKFILE
  exit
fi

echo ""
echo "*** VACUUM nodes"
$PREFIX psql "$DATABASE" -c "VACUUM VERBOSE nodes;"

echo ""
echo "*** VACUUM ways"
$PREFIX psql "$DATABASE" -c "VACUUM VERBOSE ways;"

echo ""
echo "*** VACUUM ways_nodes"
$PREFIX psql "$DATABASE" -c "VACUUM VERBOSE way_nodes;"

echo ""
echo "*** ANALYZE"
$PREFIX psql "$DATABASE" -c "ANALYZE;"

rm $LOCKFILE
