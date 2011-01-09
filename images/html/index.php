<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-15">
<link rel="stylesheet" type="text/css" href="style.css">
<title>Cartes</title>
</head>
<body class="tout">
<?
$dossier = opendir(getcwd());
while (($d = readdir($dossier)) !== FALSE) {
  if ($d != "." and $d != ".." and is_dir($d)) {
     $liste_images[] = $d;
  }
}
sort ($liste_images);

foreach ($liste_images as $d) {
  echo "<div class=\"affiche_image\"><a href=\"$d\"><img src=\"$d/thumbs/bbox.png\" title=\"$d\"><br>$d</a></div>\n";
}
closedir($dossier);
?>
</body>
</html>

