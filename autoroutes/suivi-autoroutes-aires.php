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
  <title>Aires d'autoroute en date du $date</title>
</head>
<body>
<style type=\"text/css\">
<!--
td.a0_50 { color: red; }
td.a50_80 { color: orange; }
/* normal color for 80-95 */
td.a95_ { color: green; }
-->
</style>
<h2>Etat d'avancement des aires des autoroutes en date du $date</h2>
<p>Liste des nodes qui contiennent un tag highway=services ou highway=rest_area et qui sont à moins d'un kilomètre de l'autoroute concernée.</p>
<table border='1'>
<tr>
  <th colspan=3>Relation</th>
  <th colspan=3>Node</th>
</tr>
<tr>
  <th>id_osm</th>
  <th>ref</th>
  <th>aires</th>
  <th>name</th>
  <th>highway</th>
  <th>distance<br>(mètres)</th>
  <th>id</th>
</tr>\n";

$csv = "\n";

$query_autoroutes="
SELECT relation_id, relation_ref,
       name, node_id, distance, highway,
       (SELECT COUNT(a.node_id) FROM osm_autoroutes_aires a
        WHERE a.relation_id = b.relation_id) AS num_aires
FROM osm_autoroutes_aires b
ORDER BY id, relation_ref, name;
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
  <td>$autoroute->relation_ref</td>
  <td>$autoroute->num_aires</td>
");
  } else {
    print ("<tr>
  <td></td>
  <td></td>
  <td></td>
");
  }
  print "  <td>$autoroute->name</td>\n";
  print "  <td>$autoroute->highway</td>\n";
  print "  <td>$autoroute->distance</td>\n";

  $osm_id = $autoroute->node_id;
  print ("<td><a href='http://www.openstreetmap.org/browse/node/$osm_id'>$osm_id</a>&nbsp;<a href='http://localhost:8111/import?url=http://api.openstreetmap.org/api/0.6/node/$osm_id' target='suivi-josm'>josm</a></td>");

  print ("  </td>");
  print ("</tr>\n");
}

print "</table>\n";
print "</body>";
print "</html>";

