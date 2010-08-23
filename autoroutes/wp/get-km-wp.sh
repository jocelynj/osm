#! /bin/sh

for i in `cat liste | sort -n -t"A" -k2`; do
  id=`echo $i | tr -d "A"`
  km=`grep -A1 '<th align="left">Longueur' Autoroute_française_$i | grep td | sed "s/<td>\([0-9.,]*\).*/\1/" | tr "," "." | tr -d "\n"`
  if [ "x$km" = "x" ]; then
    km=0
  fi
  echo "$id;A $id;$km"
done > km-autoroutes

cat km-autoroutes

psql osm << PSQL
TRUNCATE autoroutes;
\\copy autoroutes from 'km-autoroutes' with delimiter as ';'
PSQL

