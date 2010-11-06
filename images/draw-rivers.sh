#! /bin/bash

. ./draw-functions.sh

get_line_shp rivers.shp "tags->'waterway' != 'stream'"
get_polygon_shp rivers2.shp "tags->'waterway' != 'stream'"
get_polygon_shp rivers3.shp "(tags->'natural' = 'water' OR tags->'landuse' = 'reservoir') AND
                             ST_Area(geography(ST_MakePolygon(linestring))) > 100"

./create_tif.py coastline.shp rivers.tif

draw_shp rivers.tif border.shp 200 200 0

draw_shp rivers.tif rivers.shp 100 100 255
draw_shp rivers.tif rivers2.shp 100 100 255
draw_shp rivers.tif rivers3.shp 50 50 255

draw_shp rivers.tif coastline.shp 200 200 255

