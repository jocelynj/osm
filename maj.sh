#! /bin/sh

set -e

date

(cd osmosis && ./update-pgsql.sh && psql osm < CreateGeometryForWays-relations.sql) || exit

date

(cd autoroutes && ./maj.sh)
(cd rivieres && ./maj.sh)

date
