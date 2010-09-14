#! /bin/bash

. ./draw-functions.sh

get_line_shp france-coastline.shp "k = 'natural' AND v='coastline'"

./create_tif.py france-coastline.shp france-coastline.tif
draw_shp france-coastline.tif france-coastline.shp 200 200 255
