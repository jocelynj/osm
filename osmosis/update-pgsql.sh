#! /bin/bash
set -e

PREFIX=/usr/bin/time

CHANGEFILE="change-`date +%F`.osc.gz"

rm -f $CHANGEFILE
$PREFIX osmosis --read-change-interval --write-xml-change $CHANGEFILE

change_size=`stat -c "%s" $CHANGEFILE`
if [ $change_size -le 1000 ]; then
  exit 1
fi

# The bounding box to maintain.
LEFT=-5.5163122
BOTTOM=41.0945041
RIGHT=10.1696967
TOP=51.3336307

$PREFIX osmosis --read-xml-change $CHANGEFILE --simplify-change --sort-change \
                --fast-read-xml france.osm.gz --apply-change --buffer \
                --tf reject-ways "building=*" \
                --bounding-box left=$LEFT bottom=$BOTTOM right=$RIGHT top=$TOP \
                --write-xml france2.osm.gz

mv france2.osm.gz france.osm.gz

$PREFIX osmosis --fast-read-xml france.osm.gz --write-pgsql-dump

$PREFIX psql osm < ./pgsql_simple_load_0.6.sql

