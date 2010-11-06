#! /bin/bash

. ./draw-functions.sh

get_line_shp coastline.shp "tags->'natural' = 'coastline'"

./create_tif.py coastline.shp coastline.tif
draw_shp coastline.tif coastline.shp 200 200 255
