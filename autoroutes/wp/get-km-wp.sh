#! /bin/sh

for i in `cat liste | sort -n -t"A" -k2`; do
  id=`echo $i | tr -d "A"`
  km=`grep -A1 '<th align="left">Longueur' Autoroute_française_$i | grep td | sed "s/<td>\([0-9.,]*\).*/\1/" | tr "," "." | tr -d "\n"`
  if [ "x$km" = "x" ]; then
    km=0
  fi
  echo "$id;A $id;$km"
done > km-autoroutes

psql osm << PSQL
TRUNCATE autoroutes;
\\copy autoroutes from 'km-autoroutes' with delimiter as ';'
-- corrections
UPDATE autoroutes SET longueur=394 WHERE id=26  AND longueur=0;
UPDATE autoroutes SET longueur=55  WHERE id=72  AND longueur=0;
UPDATE autoroutes SET longueur=12.5 WHERE id=105;
UPDATE autoroutes SET longueur=13  WHERE id=115 AND longueur=0;
UPDATE autoroutes SET longueur=34  WHERE id=131 AND longueur=0;
UPDATE autoroutes SET longueur=6.5 WHERE id=132 AND longueur=0;
UPDATE autoroutes SET longueur=3   WHERE id=139 AND longueur=0;
UPDATE autoroutes SET longueur=9   WHERE id=140 AND longueur=0;
UPDATE autoroutes SET longueur=3.5 WHERE id=211;
UPDATE autoroutes SET longueur=21  WHERE id=660 AND longueur=0;
UPDATE autoroutes SET longueur=7   WHERE id=710;
UPDATE autoroutes SET longueur=1   WHERE id=712;
UPDATE autoroutes SET longueur=9.6 WHERE id=714;

-- non construites
DELETE FROM autoroutes WHERE id=112;

-- depuis wikisara
UPDATE autoroutes SET longueur=74  WHERE id=86  AND longueur=0;
UPDATE autoroutes SET longueur=8   WHERE id=680;
PSQL

