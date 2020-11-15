#! /bin/bash

POLY=$1
WORKDIR=/data/work/osmbin/extracts/$POLY

CURDATE="`date +%F-%R`"

LOCKFILE="$WORKDIR/lock-osmium-maj"
LOGFILE="$WORKDIR/replication-${CURDATE}.log"
ERRFILE="$WORKDIR/replication-${CURDATE}.err"
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

echo "*** Update $SOURCE_OSM_FILE"
pyosmium-up-to-date -v "$SOURCE_OSM_FILE" -o "$TARGET_OSM_FILE"
if [ $? -ne 0 ]; then
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

osmium fileinfo "$SOURCE_OSM_FILE" > tmp/fileinfo

SEQNUM=$(cat tmp/fileinfo | grep osmosis_replication_sequence_number= | cut -d= -f2)
TIMESTAMP=$(cat tmp/fileinfo | grep osmosis_replication_timestamp= | cut -d= -f2 | sed s/:/\\\\:/g)

cat << EOF > state.txt
sequenceNumber=$SEQNUM
timestamp=$TIMESTAMP
EOF

rm "$TARGET_OSM_FILE"
rm "${TARGET_OSM_FILE}.md5"
rm "tmp/fileinfo"

rm $LOCKFILE
