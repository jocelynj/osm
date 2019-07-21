#! /bin/bash

set -e

G_WORKDIR=/data/work/osmbin/replication/diffs/

cd polygons

minute_dirs=$(find -name "*.poly" | sed "s%.poly%/minute%")

cd $G_WORKDIR

num=$(cat planet/minute/state.txt | grep sequenceNumber | cut -d= -f2)
oldest=$(($num - 3*30*24*60))  # keep 3 months of diff
oldest_dir=$(($oldest / 1000))
for d in $(seq 1000 $oldest_dir); do
  compl_dir=$(printf "%03d/%03d" $(($d / 1000)) $(($d % 1000)))
  if [ -e planet/minute/$compl_dir ]; then
    echo $compl_dir
    for c in $minute_dirs; do
      if [ -e $c/$compl_dir ]; then
#        echo $c/$compl_dir
        rm -rf $c/$compl_dir
      fi
    done
  fi
done
