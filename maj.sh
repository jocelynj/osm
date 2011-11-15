#! /bin/sh

set -e

date

(cd osmosis-hourly && ./maj.sh) || exit

echo ""
date
echo " *** autoroutes"

(cd autoroutes && ./maj.sh)

echo " *** rivieres"
(cd rivieres && ./maj.sh)
# (cd transport && ./maj.sh)

echo " *** images"
(cd images && ./maj.sh)

echo ""
date
