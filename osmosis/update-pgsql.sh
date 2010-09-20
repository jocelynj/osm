#! /bin/bash
set -e

PREFIX=/usr/bin/time
OSMOSIS="$PREFIX osmosis -q"

CHANGEFILE="change-`date +%F`.osc.gz"

rm -f $CHANGEFILE
echo ""
echo "*** Get changes from server"
$OSMOSIS --read-change-interval --write-xml-change $CHANGEFILE

change_size=`stat -c "%s" $CHANGEFILE`
if [ $change_size -le 1000 ]; then
  exit 1
fi

# The bounding box to maintain.
LEFT=-5.5163122
BOTTOM=41.0945041
RIGHT=10.1696967
TOP=51.3336307

echo ""
echo "*** Create new france.osm.gz file"
$OSMOSIS --read-xml-change $CHANGEFILE --simplify-change --sort-change \
         --fast-read-xml france.osm.gz --apply-change --buffer \
         --tf reject-ways "building=*" \
         --bounding-box left=$LEFT bottom=$BOTTOM right=$RIGHT top=$TOP \
         --write-xml france2.osm.gz

mv france2.osm.gz france.osm.gz

echo ""
echo "*** Create pgsql-dump"
$OSMOSIS --fast-read-xml france.osm.gz --write-pgsql-dump

echo ""
echo "*** Insert data in postgresql"
$PREFIX psql osm < ./pgsql_simple_load_0.6.sql

echo ""
echo "*** Recreate table way_geometry"
$PREFIX psql osm < CreateGeometryForWays-relations.sql
