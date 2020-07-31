#! /bin/bash

POLY=$1
WORKDIR=/data/work/osmbin/extracts/$POLY
OSMOSIS=/usr/bin/osmosis

CURDATE="`date +%F-%R`"

LOCKFILE="$WORKDIR/lock-osmosis-maj"
LOGFILE="$WORKDIR/replication-${CURDATE}.log"
ERRFILE="$WORKDIR/replication-${CURDATE}.err"
CHANGEFILE="$WORKDIR/change-${CURDATE}.osc.gz"
SOURCE_OSM_FILE="$WORKDIR/$(basename $POLY).osm.pbf"
TARGET_OSM_FILE="$WORKDIR/tmp/$(basename $POLY).osm.pbf"

if [ -e "$LOCKFILE" ]; then
  echo "Lock file $LOCKFILE still present - aborting update"
  exit 1
fi

touch $LOCKFILE

exec 1>"$LOGFILE"
exec 2>"$ERRFILE"

mkdir -p $WORKDIR/tmp
cd $WORKDIR

echo "*** Get changes from server"
cp "$WORKDIR/state.txt" "$WORKDIR/state.txt.old"
$OSMOSIS --read-replication-interval workingDirectory="$WORKDIR" --simplify-change --write-xml-change "$CHANGEFILE"
if [ $? -ne 0 ]; then
  cp "$WORKDIR/state.txt.old" "$WORKDIR/state.txt"
  rm $LOCKFILE
  exit 1
fi

ls -l "$CHANGEFILE"

echo "*** Update $SOURCE_OSM_FILE"
$OSMOSIS --read-xml-change "$CHANGEFILE" --read-pbf "$SOURCE_OSM_FILE" --apply-change --buffer --write-pbf file="$TARGET_OSM_FILE"
if [ $? -ne 0 ]; then
  cp "$WORKDIR/state.txt.old" "$WORKDIR/state.txt"
  rm $LOCKFILE
  exit 1
fi

(cd $(dirname "$TARGET_OSM_FILE")
 f=$(basename "$TARGET_OSM_FILE")
 md5sum "$f" > "${TARGET_OSM_FILE}.md5"
)

rm "$SOURCE_OSM_FILE"
rm "${SOURCE_OSM_FILE}.md5"
ln "$TARGET_OSM_FILE" "$SOURCE_OSM_FILE"
ln "${TARGET_OSM_FILE}.md5" "${SOURCE_OSM_FILE}.md5"

rm "$TARGET_OSM_FILE"
rm "${TARGET_OSM_FILE}.md5"
rm "$CHANGEFILE"

rm $LOCKFILE
