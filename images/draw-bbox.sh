#! /bin/bash

set -e

. ./draw-functions.sh

if [ "x$1" == "x" ]; then
  echo "Please specify boundary"
  echo "Valid values are:"
  psql $DATABASE -c "SELECT name from bounding_box"
  exit 1
else
  bbox="$1"
  cd $WORKDIR/images
fi

pgsql2shp -f bbox-$bbox.shp "$DATABASE" "
SELECT name, ST_Boundary(geom)
FROM bounding_box
WHERE name = '$bbox'"

create_tif.py bbox-$bbox.shp $bbox/bbox.tif
draw_shp $bbox/bbox.tif border.shp 200 0 0
draw_shp $bbox/bbox.tif coastline.shp 200 200 255
draw_shp $bbox/bbox.tif bbox-$bbox.shp 200 200 0

convert -quiet $bbox/bbox.tif $bbox/bbox.png
convert -quiet $bbox/bbox.tif -morphology Dilate Disk:2.0 -adaptive-resize 500x500 $bbox/thumbs/bbox.png
