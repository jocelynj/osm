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
<head>
  <title>Autoroutes en date du $date</title>
</head>
<body>
<style type=\"text/css\">
<!--
td.a0_50 { color: red; }
td.a50_80 { color: orange; }
/* normal color for 80-95 */
td.a95_ { color: green; }
td.big { background: orange; }
-->
</style>
<h2>Etat d'avancement du tracé des autoroutes en date du $date</h2>
<p>A noter que les kilométrages de référence sont prises sur Wikipédia et sur WikiSara, et ne contiennent pas toutes les autoroutes</p>
<p>Les relations prises en compte contiennent les tags suivants: type=route route=road network=FR:A-road</p>
<table border='1'>
<tr>
  <th></th>
  <th colspan=3>Longueur</th>
  <th></th>
  <th colspan=3>Infos dans OSM</th>
  <th colspan=4>km d'oneway dans OSM</th>
</tr>
<tr>
  <th>Autoroute</th>
  <th>wiki</th>
  <th>osm</th>
  <th>ratio</th>
  <th></th>
  <th>id_osm</th>
  <th>sections</th>
  <th>nom</th>
  <th>yes</th>
  <th>no</th>
  <th>(null)</th>
  <th>\"somme\"</th>
</tr>\n";

$csv = "\n";
$total_l = 0;
$total_l_osm = 0;
$prev_ref = "";

$query_autoroutes="
SELECT autoroutes.ref, autoroutes.longueur,
       relation_id, km AS osm_longueur, name, num_sections,
       km_oneway_yes, km_oneway_no, km_oneway_null
FROM autoroutes
LEFT JOIN osm_autoroutes ON autoroutes.ref = osm_autoroutes.ref
ORDER BY autoroutes.id, autoroutes.ref;
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
    if ($autoroute->num_sections) { $num_sections = $autoroute->num_sections; }
    else { $num_sections = 1; }
    if ($autoroute->km_oneway_yes) { $km_oneway_yes = round($autoroute->km_oneway_yes,1); }
    else { $km_oneway_yes = ""; }
    if ($autoroute->km_oneway_no) { $km_oneway_no = round($autoroute->km_oneway_no,1); }
    else { $km_oneway_no = ""; }
    if ($autoroute->km_oneway_null) { $km_oneway_null = round($autoroute->km_oneway_null,1); }
    else { $km_oneway_null = ""; }
    $km_oneway_sum = round($autoroute->km_oneway_no + $autoroute->km_oneway_null + $autoroute->km_oneway_yes/2, 1);
  }
  else
  {
    $avancee=0;
    $longueur_autoroute_dans_osm='';
    $osm_id="N/A";
    $osm_id_lien="N/A";
    $num_sections = "";
    $km_oneway_yes = "";
    $km_oneway_no = "";
    $km_oneway_null = "";
    $km_oneway_sum = "";
  }
  if ($prev_ref != $autoroute->ref) {
    $total_l += $autoroute->longueur;
    $l_autoroute=round($autoroute->longueur,1);
  }

  if ($l_autoroute == 0) { $l_autoroute = "";
                           $style_avancement = "";
                           $avancee = "-"; }
  else if ($avancee < 50) { $style_avancement = "a0_50"; }
  else if ($avancee < 80) { $style_avancement = "a50_80"; }
  else if ($avancee < 95) { $style_avancement = "a80_95"; }
  else if ($avancee > 105 && ($longueur_autoroute_dans_osm - $l_autoroute) > 15) {
    $style_avancement = "big";
  }
  else { $style_avancement = "a95_"; }

  print "<tr>\n";
  if ($prev_ref != $autoroute->ref) {
    $prev_ref = $autoroute->ref;
    print "  <td>$autoroute->ref</td>\n";
    print "  <td>$l_autoroute</td>\n";
  } else {
    print "  <td></td>\n";
    print "  <td></td>\n";
  }
  print "  <td>$longueur_autoroute_dans_osm</td>\n";
  print "  <td class=\"$style_avancement\">$avancee %</td>\n";
  print "  <td></td>\n";
  print "  <td>$osm_id_lien</td>\n";
  print "  <td>$num_sections</td>\n";
  print "  <td>$autoroute->name</td>\n";
  print "  <td>$km_oneway_yes</td>\n";
  print "  <td>$km_oneway_no</td>\n";
  print "  <td>$km_oneway_null</td>\n";
  print "  <td>$km_oneway_sum</td>\n";
  print "</tr>\n";
  $csv .= "$autoroute->ref;$osm_id;$l_autoroute;$longueur_autoroute_dans_osm;$avancee %;$num_sections;$autoroute->name\n";
}

$total_l = round($total_l, 1);
$total_l_osm = round($total_l_osm, 1);
$avancee = round($total_l_osm/$total_l * 100, 1);

if ($avancee < 50) { $style_avancement = "a0_50"; }
else if ($avancee < 80) { $style_avancement = "a50_80"; }
else if ($avancee < 95) { $style_avancement = "a80_95"; }
else if (($avancee > 110) and (($total_l_osm - $total_l) > 15)) { $style_avancement = "big"; }
else { $style_avancement = "a95_"; }


print "<tr>
  <td><b>Total</b></td>
  <td>$total_l</td>
  <td>$total_l_osm</td>
  <td class=\"$style_avancement\">$avancee %</td>
</tr>\n";
$csv .= "Total;;$total_l;$total_l_osm;$avancee %;;\n";

print "</table>\n";

print "<div style='display: none'>
$csv
</div>\n";
print "</body>";
print "</html>";

