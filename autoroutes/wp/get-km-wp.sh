#! /bin/sh

. ../../config

for i in `cat liste | sort -n -t"A" -k2`; do
  if [ ! -e Autoroute_française_$i ]; then
    wget http://fr.wikipedia.org/wiki/Autoroute_française_$i
  fi

  id=`echo $i | sed "s/A\([0-9]*\).*/\1/"`
  ref=`echo $i | sed "s/A\([0-9]*.*\)/A \1/"`
  km=`grep -A1 '<th align="left">Longueur' Autoroute_française_$i | grep td | sed "s/<td>\([0-9.,]*\).*/\1/" | tr "," "." | tr -d "\n"`
  if [ "x$km" = "x" ]; then
    km=0
  fi
  echo "$id;$ref;$km"
done > km-autoroutes

psql "$DATABASE" << PSQL
TRUNCATE autoroutes;
\\copy autoroutes from 'km-autoroutes' with delimiter as ';'
-- corrections
UPDATE autoroutes SET longueur=55  WHERE id=72  AND longueur=0;
UPDATE autoroutes SET longueur=12.5 WHERE id=105;
UPDATE autoroutes SET longueur=13  WHERE id=115 AND longueur=0;
UPDATE autoroutes SET longueur=34  WHERE id=131 AND longueur=0;
UPDATE autoroutes SET longueur=6.5 WHERE id=132 AND longueur=0;
UPDATE autoroutes SET longueur=3   WHERE id=139 AND longueur=0;
UPDATE autoroutes SET longueur=9   WHERE id=140 AND longueur=0;
UPDATE autoroutes SET longueur=4.5 WHERE id=391;
UPDATE autoroutes SET longueur=12.5 WHERE id=480;
UPDATE autoroutes SET longueur=1.5 WHERE id=502 AND longueur=0;
UPDATE autoroutes SET longueur=0.9 WHERE id=515 AND longueur=0;
UPDATE autoroutes SET longueur=0.9 WHERE id=516 AND longueur=0;
UPDATE autoroutes SET longueur=1.2 WHERE id=517 AND longueur=0;
UPDATE autoroutes SET longueur=5   WHERE id=621 AND longueur=0;
UPDATE autoroutes SET longueur=0.5 WHERE id=623 AND longueur=0;
UPDATE autoroutes SET longueur=4   WHERE id=624 AND longueur=0;
UPDATE autoroutes SET longueur=5   WHERE id=645 AND longueur=0;
UPDATE autoroutes SET longueur=21  WHERE id=660 AND longueur=0;
UPDATE autoroutes SET longueur=1   WHERE id=712;
UPDATE autoroutes SET longueur=9.6 WHERE id=714;

-- non construites
DELETE FROM autoroutes WHERE id=112;
DELETE FROM autoroutes WHERE id=260;
DELETE FROM autoroutes WHERE id=406;
DELETE FROM autoroutes WHERE id=507;
-- déclassées
DELETE FROM autoroutes WHERE id=401;
DELETE FROM autoroutes WHERE id=701;
DELETE FROM autoroutes WHERE id=710;
DELETE FROM autoroutes WHERE id=821;


-- depuis wikisara
UPDATE autoroutes SET longueur=10  WHERE ref='A 6a';
UPDATE autoroutes SET longueur=9   WHERE ref='A 6b';
UPDATE autoroutes SET longueur=323 WHERE id=11;
UPDATE autoroutes SET longueur=8   WHERE id=12;
UPDATE autoroutes SET longueur=361 WHERE id=26;
UPDATE autoroutes SET longueur=362 WHERE id=28;
UPDATE autoroutes SET longueur=236 WHERE id=29;
UPDATE autoroutes SET longueur=175 WHERE id=43;
UPDATE autoroutes SET longueur=47  WHERE id=46;
UPDATE autoroutes SET longueur=172 WHERE id=51;
UPDATE autoroutes SET longueur=48  WHERE id=54;
UPDATE autoroutes SET longueur=74  WHERE id=86  AND longueur=0;
UPDATE autoroutes SET longueur=48  WHERE id=88;
UPDATE autoroutes SET longueur=1   WHERE id=103;
UPDATE autoroutes SET longueur=9   WHERE id=105;
UPDATE autoroutes SET longueur=5.5 WHERE id=106;
UPDATE autoroutes SET longueur=7   WHERE id=126;
UPDATE autoroutes SET longueur=17  WHERE id=151;
UPDATE autoroutes SET longueur=7   WHERE id=154;
UPDATE autoroutes SET longueur=2   WHERE id=186;
UPDATE autoroutes SET longueur=3   WHERE id=211;
UPDATE autoroutes SET longueur=5   WHERE id=311;
UPDATE autoroutes SET longueur=2.5 WHERE id=314;
UPDATE autoroutes SET longueur=3   WHERE id=315;
UPDATE autoroutes SET longueur=4   WHERE id=340;
UPDATE autoroutes SET longueur=1.2 WHERE id=350;
UPDATE autoroutes SET longueur=5   WHERE id=351;
UPDATE autoroutes SET longueur=7   WHERE id=352;
UPDATE autoroutes SET longueur=21  WHERE id=404;
UPDATE autoroutes SET longueur=25  WHERE id=410;
UPDATE autoroutes SET longueur=2   WHERE id=411;
UPDATE autoroutes SET longueur=8   WHERE id=450;
UPDATE autoroutes SET longueur=4   WHERE id=501 AND longueur=0;
UPDATE autoroutes SET longueur=3   WHERE id=520 AND longueur=0;
UPDATE autoroutes SET longueur=1.5 WHERE id=557;
UPDATE autoroutes SET longueur=7   WHERE id=570 AND longueur=0;
UPDATE autoroutes SET longueur=19  WHERE id=620 AND longueur=0;
UPDATE autoroutes SET longueur=34  WHERE id=630;
UPDATE autoroutes SET longueur=8   WHERE id=680;

-- depuis ASF
UPDATE autoroutes SET longueur=33  WHERE id=837 AND longueur=0;

-- BP de paris
INSERT INTO autoroutes VALUES (0, 'BP', 35.5);
PSQL

