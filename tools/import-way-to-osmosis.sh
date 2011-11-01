#! /bin/bash

echo checking -$1-

if [ ! -e w$1.osm ]; then
  wget -O w$1.osm http://www.openstreetmap.org/api/0.6/way/$1/full
fi

sed 's/<osm \(.*\)$/<osmChange \1<modify>/;s#</osm>#</modify></osmChange>#' w$1.osm > w$1.osmchange

. ../config
$OSMOSIS --read-xml-change w$1.osmchange --write-pgsql-change database="$DATABASE" user="$USER" password="$PASS"
