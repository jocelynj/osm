#! /bin/sh

set -e

. ../../config

$OSMOSIS --read-xml file=$1 --buffer --write-pgsql-dump directory="$WORKDIR/tmp" enableBboxBuilder=yes enableLinestringBuilder=yes
$OSMOSIS --truncate-pgsql database="$DATABASE" user="$USER" password="$PASS"

local_dir=`pwd`

(cd "$WORKDIR/tmp" && psql "$DATABASE" -f "$local_dir/pgsnapshot_load_0.6.sql")

psql "$DATABASE" -f after_import.sql
