#! /bin/sh

set -e

date

(cd osmosis-hourly && ./maj.sh) || exit

echo ""
date
echo ""

(cd autoroutes && ./maj.sh)
(cd rivieres && ./maj.sh)
# (cd transport && ./maj.sh)
(cd images && ./maj.sh)

echo ""
date
