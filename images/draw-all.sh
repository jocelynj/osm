#! /bin/bash

. ./draw-functions.sh

for bbox in $bbox_list; do
  echo "*** $bbox"
  ./draw-bbox.sh $bbox

  for type in coastline border admin rivers rivers-relation; do
    ./draw.sh $bbox $type
  done
done
