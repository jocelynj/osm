#! /bin/sh

set -e

(cd osmosis && ./update-pgsql.sh && psql osm < CreateGeometryForWays-relations.sql) || exit

(cd autoroutes && ./maj.sh)
