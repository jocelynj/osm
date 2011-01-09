<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-15">
<link rel="stylesheet" type="text/css" href="../style.css">
<title>Cartes</title>
</head>
<body class="pays">
<?
$dossier = opendir(getcwd());
while (($d = readdir($dossier)) !== FALSE) {
  if (!is_dir($d) and strpos($d, ".png") !== false) {
     $liste_images[] = $d;
  }
}
sort ($liste_images);

foreach ($liste_images as $d) {
  echo "<div class=\"affiche_image\"><a href=\"$d\"><img src=\"thumbs/$d\" title=\"$d\"><br>$d</a></div>\n";
}
closedir($dossier);
?>
</body>
</html>

