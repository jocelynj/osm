<?php
/*
Ce script est distribué sous licence BSD
*/

/* Petite bidouille pour fournir le code source de moi même si ?src est passé en paramètre */
if (isset($_GET['src']))
{
  header("Content-Type: text/plain"); // de toute façon ça se lance dans un cron, sauf cas du :
  die(file_get_contents($_SERVER['SCRIPT_FILENAME'])); 
}
else
  header("Content-type: text/html; charset=UTF-8");

include("../config.php");

print "<html>
<head>
  <meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\"/>
  <title>Sorties d'autoroute en date du $date</title>
</head>
<body>
<style type=\"text/css\">
<!--
td.a0_50 { color: red; }
td.a50_80 { color: orange; }
/* normal color for 80-95 */
td.a95_ { color: green; }
.orange { background: orange; }
-->
</style>
<h2>Etat d'avancement des sorties des autoroutes en date du $date</h2>
<p>Liste des nodes qui contiennent un tag highway et qui sont sur l'autoroute concernée.</p>
<p>Les nodes en <span class='orange'>orange</span> sont les nodes qui n'ont pas un des tags parmi <b>ref</b>, <b>name</b> ou <b>exit_to</b>.</p>
<table border='1'>
<tr>
  <th colspan=2>Relation</th>
  <th colspan=4>Nodes</th>
</tr>
<tr>
  <th>id_osm</th>
  <th>ref</th>
  <th>ref</th>
  <th>name</th>
  <th>total</th>
  <th>id</th>
</tr>\n";

$csv = "\n";

$query_autoroutes="
SELECT relation_id, relation_ref,
       ref, name, exit_to,
       total, nodes_id
FROM osm_autoroutes_sorties
ORDER BY id, relation_ref, int4(regexp_replace(ref, '^([0-9]*).*', E'0\\\\1')), ref, name
";

$prev_autoroute = -1;

$res_autoroutes=pg_query($query_autoroutes);

while($autoroute=pg_fetch_object($res_autoroutes))
{
  $osm_id=$autoroute->relation_id;
  $osm_id_lien="<a href='http://www.openstreetmap.org/browse/relation/$osm_id'>$osm_id</a>&nbsp;<a href='http://localhost:8111/import?url=http://api.openstreetmap.org/api/0.6/relation/$osm_id/full' target='suivi-josm'>josm</a>";

  if ($prev_autoroute != $autoroute->relation_ref) {
    $prev_autoroute = $autoroute->relation_ref;
    print ("<tr>
  <td>$osm_id_lien</td>
  <td><a name='$autoroute->relation_ref'>$autoroute->relation_ref</a></td>
");
  } else {
    print ("<tr>
  <td></td>
  <td></td>
");
  }
  print "  <td>$autoroute->ref</td>\n";
  if ($autoroute->exit_to) {
    $exit_to = "<p><b>exit_to:</b> $autoroute->exit_to</p>";
  } else {
    $exit_to = "";
  }
  print "  <td>$autoroute->name $exit_to</td>\n";
  print "  <td>$autoroute->total</td>\n";

  if ($autoroute->ref == "" && $autoroute->name == "" && $autoroute->exit_to == "") {
    print ("<td><table class='orange'><tr>");
  } else {
    print ("<td><table><tr>");
  }

  $nodes = explode('-', $autoroute->nodes_id);
  for($i = 1; $i<count($nodes); $i++) {
    $osm_id = $nodes[$i];
    print ("<td><a href='http://www.openstreetmap.org/browse/node/$osm_id'>$osm_id</a>&nbsp;<a href='http://localhost:8111/import?url=http://api.openstreetmap.org/api/0.6/node/$osm_id' target='suivi-josm'>josm</a></td>");
    if ($i % 5 == 0) {
      print ("</tr><tr>");
    }
  }

  print ("</tr></table></td>");
  print ("</tr>\n");
}

print "</table>\n";
print "</body>";
print "</html>";

