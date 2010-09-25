#! /bin/sh

set -e

date

(cd osmosis && ./update-pgsql.sh) || exit

echo ""
date
echo ""

(cd autoroutes && ./maj.sh)
(cd rivieres && ./maj.sh)
(cd transport && ./maj.sh)

echo ""
date
