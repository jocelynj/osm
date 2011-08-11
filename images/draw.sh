#! /bin/bash

set -e

. ./draw-functions.sh

if [ "x$1" = "x" ]; then
  echo "Please specify boundary"
  echo "Valid values are:"
  psql $DATABASE -c "SELECT name from bounding_box"
  exit 1
else
  bbox="$1"
  cd $WORKDIR/images
fi

if [ "x$2" = "x" ]; then
  echo "Please specify what to draw"
  exit 1
fi
type=$2

img=$bbox/$type.tif

create_tif.py bbox-$bbox.shp $img

case "$type" in
  "coastline")
    draw_shp $img coastline.shp 200 200 255
    ;;

  "border")
    draw_shp $img border.shp 200 200 0
    draw_shp $img coastline.shp 200 200 255
    ;;

  "admin")
    draw_shp $img admin_6.shp 250 210 100
    draw_shp $img admin_4.shp 220 20 90
    draw_shp $img border.shp 200 200 0
    draw_shp $img coastline.shp 200 200 255
    ;;

  "rivers")
    draw_shp $img border.shp 200 200 0

    draw_shp $img rivers_line.shp 100 100 255
    draw_shp $img rivers_polygon.shp 100 100 255
    draw_shp $img rivers_lake.shp 50 50 255

    draw_shp $img rivers-relation-tributary.shp 200 255 200
    gdal_rasterize -b 1 -burn 255 -l rivers-relation rivers-relation.shp $img

    draw_shp $img coastline.shp 200 200 255
    ;;

  "rivers-relation")
    draw_shp $img rivers-relation-tributary.shp 200 255 200
    gdal_rasterize -b 1 -burn 255 -l rivers-relation rivers-relation.shp $img
    draw_shp $img coastline.shp 200 200 255
    ;;

  default)
    echo "action $type not valid"
    exit 1
    ;;

esac

convert -quiet $img $bbox/$type.png
convert -quiet $img -morphology Dilate Disk:2.0 -adaptive-resize 500x500 $bbox/thumbs/$type.png
