#! /bin/bash

set -e

. ./draw-functions.sh

for bbox in $bbox_list; do
  echo "*** $bbox"
  mkdir -p $WORKDIR/images/$bbox/thumbs
  ./draw-bbox.sh $bbox

  for type in coastline border admin rivers rivers-relation motorway; do
    ./draw.sh $bbox $type
  done
done
