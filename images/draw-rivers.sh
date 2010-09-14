#! /bin/bash

. ./draw-functions.sh

get_line_shp france-rivers.shp "k = 'waterway' AND v != 'stream'"
get_polygon_shp france-rivers2.shp "k = 'waterway' AND v != 'stream'"
get_polygon_shp france-rivers3.shp "k = 'natural' AND v = 'water' AND
                                    ST_Area(geography(way_geom(way_id))) > 1000000"

./create_tif.py france-coastline.shp france-rivers.tif

draw_shp france-rivers.tif france-rivers.shp 100 100 255
draw_shp france-rivers.tif france-rivers2.shp 100 100 255
draw_shp france-rivers.tif france-rivers3.shp 50 50 255

draw_shp france-rivers.tif france-border.shp 200 200 0
draw_shp france-rivers.tif france-coastline.shp 200 200 255

