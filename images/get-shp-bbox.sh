#! /bin/bash

. ./draw-functions.sh

if [ "x$1" == "x" ]; then
  echo "Please specify boundary"
  echo "Valid values are:"
  psql $DATABASE -c "SELECT name from bounding_box"
  exit 1
else
  bbox="$1"
  cd $WORKDIR/images
  mkdir -p $bbox/thumbs
fi

pgsql2shp -f bbox-$bbox.shp "$DATABASE" "
SELECT name, ST_Boundary(geom)
FROM bounding_box
WHERE name = '$bbox'"
