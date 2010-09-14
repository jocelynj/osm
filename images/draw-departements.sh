#! /bin/bash

. ./draw-functions.sh

get_line_shp france-region.shp "wt1.k = 'admin_level' AND wt1.v='4'" \
                               "wt2.k = 'maritime'" "wt2.v IS NULL"
get_line_shp france-departement.shp "wt1.k = 'admin_level' AND wt1.v='6'" \
                                    "wt2.k = 'maritime'" "wt2.v IS NULL"

./create_tif.py france-coastline.shp france-departement.tif

draw_shp france-departement.tif france-departement.shp 250 210 100
draw_shp france-departement.tif france-region.shp 220 20 90
draw_shp france-departement.tif france-border.shp 200 200 0
draw_shp france-departement.tif france-coastline.shp 200 200 255


