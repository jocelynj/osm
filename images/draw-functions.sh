#!/bin/bash

. ../config

#bbox_list="france_metro haiti guadeloupe guyane martinique reunion"
#bbox_list="guadeloupe guyane martinique reunion mayotte saint-barthelemy saint-pierre-et-miquelon polynesie-francaise wallis-et-futuna"
bbox_list=`psql "$DATABASE" -t -c "select name from bounding_box;"`

export PATH=$PATH:`pwd`

function get_line_shp {
  # $1 is the target file
  # $2 is the SQL argument to the WHERE function
  # $3 is an optional SQL argument to check another tag
  sql="SELECT id, linestring AS geom
FROM ways"

  sql="$sql
WHERE $2 AND
      ST_NumPoints(linestring) > 2"
  if [ "x$3" != "x" ]; then
    sql="$sql AND $3 "
  fi
  if [ "x$4" != "x" ]; then
    sql="$sql AND $4 "
  fi

  echo "$sql"

  pgsql2shp -f "$1" "$DATABASE" "$sql"
}  

function get_polygon_shp {
  # $1 is the target file
  # $2 is the SQL argument to the WHERE function
  pgsql2shp -f "$1" "$DATABASE" "
SELECT id, ST_MakePolygon(linestring) AS geom
FROM ways
WHERE $2 AND
      ST_IsClosed(linestring) AND
      ST_NumPoints(linestring) >= 4
"
}  

function draw_shp {
  # $1 is the target .tif file
  # $2 is the source .shp file
  # $3 $4 $5 are the RGB colours to write

  layer=`echo "$2" | sed "s/.shp$//"`
  gdal_rasterize -b 1 -b 2 -b 3 -burn "$3" -burn "$4" -burn "$5" \
                 -l "$layer" "$2" "$1"
}
