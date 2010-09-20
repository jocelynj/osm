#! /bin/sh

set -e

date

(cd osmosis && ./update-pgsql.sh) || exit

date

(cd autoroutes && ./maj.sh)
(cd rivieres && ./maj.sh)

date
