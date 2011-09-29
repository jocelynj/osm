#! /bin/sh

echo "Script should not be directly executed"
exit 0

. ../config

createuser $USER
createdb $DATABASE
createlang plpgsql $DATABASE

psql -U postgres "$DATABASE" -f /usr/share/postgresql/8.4/contrib/hstore.sql
psql -U postgres "$DATABASE" -f /usr/share/postgresql/8.4/contrib/postgis-1.5/postgis.sql
psql -U postgres "$DATABASE" -f /usr/share/postgresql/8.4/contrib/postgis-1.5/spatial_ref_sys.sql
psql -U postgres "$DATABASE" -c "ALTER TABLE spatial_ref_sys OWNER TO $USER"
psql -U postgres "$DATABASE" -c "ALTER TABLE geography_columns OWNER TO $USER"
psql -U postgres "$DATABASE" -c "ALTER TABLE geometry_columns OWNER TO $USER"

psql -U "$USER" "$DATABASE" -f "$OSMOSIS_DIR/script/pgsimple_schema_0.6.sql"
psql -U "$USER" "$DATABASE" -f "$OSMOSIS_DIR/script/pgsimple_schema_0.6_bbox.sql"
psql -U "$USER" "$DATABASE" -f "$OSMOSIS_DIR/script/pgsimple_schema_0.6_linestring.sql"

# change state number to the correct one
cd "$WORKDIR"
$OSMOSIS --read-replication-interval-init
sed -i "s#/minute-replicate#/hour-replicate#" configuration.txt
sed -i "s/\(maxInterval =\).*/\1 172800/" configuration.txt
wget -O state.txt http://planet.openstreetmap.org/hour-replicate/000/008/278.state.txt
wget -c http://download.geofabrik.de/osm/europe.osm.pbf

$OSMOSIS --read-pbf file=europe.osm.pbf --fast-write-pgsql database="$DATABASE" user="$USER" password="$PASS"
$OSMOSIS --read-pbf file=europe.osm.pbf --log-progress --write-pgsql database="$DATABASE" user="$USER" password="$PASS"
