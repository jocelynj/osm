#! /bin/bash

. ./draw-functions.sh

get_line_shp france-border.shp "wt1.k = 'admin_level' AND wt1.v='2'" \
                               "wt2.k = 'maritime'" "wt2.v IS NULL"

./create_tif.py france-coastline.shp france-border.tif
draw_shp france-border.tif france-border.shp 200 200 0
draw_shp france-border.tif france-coastline.shp 200 200 255

