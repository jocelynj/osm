#! /bin/sh

echo "Script should not be directly executed"
exit 0

. ../config

psql -U postgres "$DATABASE" -f /usr/share/postgresql/8.4/contrib/hstore.sql 

createuser osmosis
createdb osmosis
psql -U "$USER" "$DATABASE" -f "$OSMOSIS_DIR/script/pgsql_simple_schema_0.6.sql"
psql -U "$USER" "$DATABASE" -f "$OSMOSIS_DIR/script/pgsql_simple_schema_0.6_bbox.sql"
psql -U "$USER" "$DATABASE" -f "$OSMOSIS_DIR/script/pgsql_simple_schema_0.6_linestring.sql"

# change state number to the correct one
cd "$WORKDIR"
wget -O state.txt http://planet.openstreetmap.org/hour-replicate/000/008/278.state.txt
wget -c http://download.geofabrik.de/osm/europe.osm.pbf

osmosis --read-pbf europe.osm.pbf --fast-write-pgsql database="$DATABASE" user="$USER" password="$PASSWORD"
