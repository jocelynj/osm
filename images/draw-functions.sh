#!/bin/bash

function get_line_shp {
  # $1 is the target file
  # $2 is the SQL argument to the WHERE function
  # $3 is an optional SQL argument to check another tag
  sql="SELECT wt1.way_id, way_geom(wt1.way_id) AS geom
FROM way_tags wt1"

  if [ "x$3" != "x" ]; then
    sql="$sql
LEFT JOIN way_tags wt2 ON wt1.way_id = wt2.way_id AND $3 "
  fi
  sql="$sql
WHERE $2 AND
      ST_NumPoints(way_geom(wt1.way_id)) > 2"
  if [ "x$4" != "x" ]; then
    sql="$sql
AND $4 "
  fi

  echo "$sql"

  pgsql2shp -f "$1" osm "$sql"
}  

function get_polygon_shp {
  # $1 is the target file
  # $2 is the SQL argument to the WHERE function
  pgsql2shp -f "$1" osm "
SELECT way_id, ST_MakePolygon(way_geom(way_id)) AS geom
FROM way_tags
WHERE $2 AND
      ST_IsClosed(way_geom(way_id)) AND
      ST_NumPoints(way_geom(way_id)) >= 4
"
}  

function draw_shp {
  # $1 is the target .tif file
  # $2 is the source .shp file
  # $3 $4 $5 are the RGB colours to write

  layer=`echo "$2" | sed "s/.shp$//"`
  gdal_rasterize -b 1 -b 2 -b 3 -burn "$3" -burn "$4" -burn "$5" \
                 -l "$layer" "$2" "$1"
  png=`echo $1 | sed "s/.tif$/.png/"`
  convert $1 $png

}
