#! /bin/bash

. ./draw-functions.sh

get_line_shp border.shp "tags->'admin_level' = '2'" \
                        "NOT tags ? 'maritime'"

./create_tif.py coastline.shp border.tif
draw_shp border.tif border.shp 200 200 0
draw_shp border.tif coastline.shp 200 200 255

