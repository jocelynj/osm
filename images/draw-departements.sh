#! /bin/bash

. ./draw-functions.sh

get_line_shp admin_4.shp "tags->'admin_level' = '4' AND NOT tags ? 'maritime'"
get_line_shp admin_6.shp "tags->'admin_level' = '6' AND NOT tags ? 'maritime'"

./create_tif.py coastline.shp admin_6.tif

draw_shp admin_6.tif admin_6.shp 250 210 100
draw_shp admin_6.tif admin_4.shp 220 20 90
draw_shp admin_6.tif border.shp 200 200 0
draw_shp admin_6.tif coastline.shp 200 200 255


