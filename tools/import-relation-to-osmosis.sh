#! /bin/bash

echo checking -$1-

if [ ! -e r$1.osm ]; then
  wget -O r$1.osm http://www.openstreetmap.org/api/0.6/relation/$1/full
fi

#     <member type="relation" ref="1047206" role=""/>

if [ "x$2" != "xalone" -a `grep 'member type="relation"' r$1.osm | wc -l` -gt 0 ]; then
  grep 'member type="relation"' r$1.osm | \
    sed 's/.*"relation" ref="\([0-9]*\)".*/\1/' | \
    xargs -n1 ./import-relation-to-osmosis.sh
fi

sed 's/<osm \(.*\)$/<osmChange \1<modify>/;s#</osm>#</modify></osmChange>#' r$1.osm > r$1.osmchange

. ../config
$OSMOSIS --read-xml-change r$1.osmchange --write-pgsql-change database="$DATABASE" user="$USER" password="$PASS"
