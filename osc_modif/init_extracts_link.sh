#! /bin/bash

set -e

G_WORKDIR=/data/work/osmbin/extracts/
WEBDIR=/data/project/osmbin/web/extracts
POLYDIR=$HOME/osm/osc_modif/polygons
MERGEDIR=$HOME/osm/osc_modif/merge

for region in $(cd $POLYDIR && ls | grep -v ".poly"); do
  echo "*** Init link for $region"
  mkdir -p $WEBDIR/$region

  for p in $(cd $POLYDIR/$region && find -name "*.poly" | sed 's#.poly$##'); do
    name=$(basename $p)
    mkdir -p $(dirname $WEBDIR/$region/$p)
    ln -sf $G_WORKDIR/$region/$p/$name.osm.pbf $WEBDIR/$region/$p.osm.pbf
    ln -sf $G_WORKDIR/$region/$p/$name.osm.pbf $WEBDIR/$region/$p-latest.osm.pbf
    ln -sf $G_WORKDIR/$region/$p/state.txt $WEBDIR/$region/$p.state.txt
  done

  if [ -e $POLYDIR/$region.poly -a -e $G_WORKDIR/$region/state.txt -a -e $G_WORKDIR/$region/$region.osm.pbf ]; then
    ln -sf $G_WORKDIR/$region/$region.osm.pbf $WEBDIR/$region.osm.pbf
    ln -sf $G_WORKDIR/$region/$region.osm.pbf.md5 $WEBDIR/$region.osm.pbf.md5
    ln -sf $G_WORKDIR/$region/$region.osm.pbf $WEBDIR/$region-latest.osm.pbf
    ln -sf $G_WORKDIR/$region/$region.osm.pbf.md5 $WEBDIR/$region-latest.osm.pbf.md5
    ln -sf $G_WORKDIR/$region/state.txt $WEBDIR/$region.state.txt
  fi

done

G_WORKDIR=$G_WORKDIR/merge
WEBDIR=$WEBDIR/merge

for region in $(cd $MERGEDIR && ls); do
  echo "*** Init link for merge/$region"
  mkdir -p $WEBDIR

  if [ -e $MERGEDIR/$region -a -e $G_WORKDIR/$region/state.txt -a -e $G_WORKDIR/$region/$region.osm.pbf ]; then
    ln -sf $G_WORKDIR/$region/$region.osm.pbf $WEBDIR/$region.osm.pbf
    ln -sf $G_WORKDIR/$region/$region.osm.pbf $WEBDIR/$region-latest.osm.pbf
    ln -sf $G_WORKDIR/$region/state.txt $WEBDIR/$region.state.txt
  fi

done
