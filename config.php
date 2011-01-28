<?

//if (!$c=pg_connect("dbname=osmosis host=localhost user=osmosis password=osmosis"))
if (!$c=pg_connect("dbname=osmosis"))
  die("Erreur connexion SQL");

$date=exec('cat /data/work/osmosis/state.txt | sed s/timestamp=// | sed s/\\\\\\\\//g | sed s/[TZ]/" "/g');

?>
