#! /bin/sh

POLYDIR=$HOME/osm/osc_modif/polygons
MERGEDIR=$HOME/osm/osc_modif/merge

WORKDIR=/data/work/osmbin/extracts/
LOCKFILE="$WORKDIR/lock-update_pbf_all"

date

exec 8>$LOCKFILE;

if flock -n -e 8; then :
else
  echo "Lock file $LOCKFILE still present - aborting update"
  exit 1;
fi

for i in $(cd $POLYDIR && find -name "*.poly" | sed 's#.poly$##'); do
  echo $i
  sem -j 4 ./update_pbf.sh $i
done

for i in $(cd $MERGEDIR && find ); do
  echo merge/$i
  sem -j 4 ./update_pbf.sh merge/$i
done

sem --wait

date

rm $LOCKFILE
