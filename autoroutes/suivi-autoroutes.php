<?php
/*
Ce script est distribué sous licence BSD avec une clause particulière :
L'utilisation, la modification et la distribution est interdite à toute personne en cours de rédaction d'un mémoire de
thèse et qui aurrait pris du retard dans sa rédaction.

L'auteur décline toute responsabilité quant au temps perdu et aux cheveux arrachés à tenter de comprendre ce code.

--
sly

 script de statistiques des autoroutes
 oui, tout en un, c'est moyen mais voilà.
 Pour chaque autoroute :
 - Obtenir la liste des cours d'eau et leur longueur gràce à wikipedia
 - comparer les deux et établir un état d'avancement
*/

/* Petite bidouille pour fournir le code source de moi même si ?src est passé en paramètre */
if (isset($_GET['src']))
{
  header("Content-Type: text/plain"); // de toute façon ça se lance dans un cron, sauf cas du :
  die(file_get_contents($_SERVER['SCRIPT_FILENAME'])); 
}
else
  header("Content-type: text/html; charset=UTF-8");

if (!$c=pg_connect("dbname=osm host=localhost user=osm password=osm"))
  die("Erreur connexion SQL");

$date=exec('cat /home/jocelyn/gps/osm/france/osmosis/timestamp.txt | sed s/timestamp=// | sed s/\\\\\\\\//g | sed s/[TZ]/" "/g');

print "<html>
<style type=\"text/css\">
<!--
td.a0_50 { color: red; }
td.a50_80 { color: orange; }
/* normal color for 80-95 */
td.a95_ { color: green; }
-->
</style>
<p>Etat d'avancement du tracé des autoroutes en date du $date</p>
<p>A noter que les kilométrages de référence sont prises sur Wikipédia, et ne contiennent pas toutes les autoroutes</p>
<p>Les relations prises en compte contiennent les tags suivants: type=route route=road network=FR:A-road</p>
<table border='1'>
<tr>
  <th></th>
  <th></th>
  <th colspan=3>Longueur</th>
  <th></th>
  <th colspan=2>Infos dans OSM</th>
</tr>
<tr>
  <th>Autoroute</th>
  <th>id_osm</th>
  <th>wp</th>
  <th>osm</th>
  <th>ratio</th>
  <th></th>
  <th>sections</th>
  <th>nom</th>
</tr>\n";

$csv = "\n";
$total_l = 0;
$total_l_osm = 0;

$query_autoroutes="
SELECT autoroutes.ref, autoroutes.longueur,
       relation_id, km AS osm_longueur, name, num_sections
FROM autoroutes
LEFT JOIN osm_autoroutes ON autoroutes.ref = osm_autoroutes.ref
ORDER BY autoroutes.id;
";

$res_autoroutes=pg_query($query_autoroutes);

while($autoroute=pg_fetch_object($res_autoroutes))
{
  if ($autoroute->relation_id > 0) {
    $total_l_osm += $autoroute->osm_longueur;
    $longueur_autoroute_dans_osm=round($autoroute->osm_longueur,1);
    $avancee=round($autoroute->osm_longueur/$autoroute->longueur*100,1);
    $osm_id=$autoroute->relation_id;
    $osm_id_lien="<a href='http://www.openstreetmap.org/browse/relation/$osm_id'>$osm_id</a>
    <a href='http://localhost:8111/import?url=http://api.openstreetmap.org/api/0.6/relation/$osm_id/full' target='suivi-josm'>josm</a>";

  }
  else
  {
    $avancee=0;
    $longueur_autoroute_dans_osm='';
    $osm_id="N/A";
    $osm_id_lien="N/A";
  }
  $total_l += $autoroute->longueur;
  $l_autoroute=round($autoroute->longueur,1);

  if ($l_autoroute == 0) { $style_avancement = "";
                           $avancee = "-"; }
  else if ($avancee < 50) { $style_avancement = "a0_50"; }
  else if ($avancee < 80) { $style_avancement = "a50_80"; }
  else if ($avancee < 95) { $style_avancement = "a80_95"; }
  else { $style_avancement = "a95_"; }

  print ("<tr>
  <td>$autoroute->ref</td>
  <td>$osm_id_lien</td>
  <td>$l_autoroute</td>
  <td>$longueur_autoroute_dans_osm</td>
  <td class=\"$style_avancement\">$avancee %</td>
  <td></td>
  <td>$autoroute->num_sections</td>
  <td>$autoroute->name</td>
</tr>\n");
  $csv .= "$autoroute->ref;$osm_id;$l_autoroute;$longueur_autoroute_dans_osm;$avancee %;$autoroute->num_sections;$autoroute->name\n";
}

$total_l = round($total_l, 1);
$total_l_osm = round($total_l_osm, 1);
$avancee = round($total_l_osm/$total_l * 100, 1);
print "<tr>
  <td><b>Total</b></td>
  <td></td>
  <td>$total_l</td>
  <td>$total_l_osm</td>
  <td class=\"$style_avancement\">$avancee %</td>
</tr>\n";
$csv .= "Total;;$total_l;$total_l_osm;$avancee %;;\n";

print "</table>\n";

print "<div style='display: none'>
$csv
</div>\n";
print "</html>";

