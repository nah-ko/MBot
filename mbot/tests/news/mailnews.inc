<?
/*
$Id$

PHP script for mbot NewsHandler
Author: Christophe Truffier <toffe@nah-ko.org>

Useful if you want to display quickly datas on your website.
*/
require ($_SERVER["DOCUMENT_ROOT"]."/SQL.inc");

$site	= "test";
$base	= "db";
$table	= "news_test";

function debug($ch) {
	global $debug;
	if ($debug)
		echo $ch;
}

function connect() {
	global $serveur_SQL, $user, $user_pass;
	mysql_connect($serveur_SQL,$user,$user_pass)
	or die( 'Connexion au serveur [<FONT COLOR=RED>Impossible</FONT> ]' );
	debug( 'Connexion au serveur [<FONT COLOR=RED>OK</FONT> ]<BR>' );
}

function reformatedate($ladate) {
	setlocale ("LC_ALL", "fr_FR");
	$reponse = strftime("Le %A %d %B %Y &agrave; %Hh%M:%S",strtotime($ladate));
	$reponse = strftime("%D %T",strtotime($ladate));
	debug( 'Reformatage de la date [<FONT COLOR=RED>OK</FONT> ]<BR>' );
	return $reponse;
}

function affichesujet($site, $base, $table) {
	connect();
	$requete = "select date, sujet from ".$table." where site='".$site."' order by id desc limit 5";
	$resultat = mysql_db_query($base, $requete)
	or die( 'affichesujet: Execution de la requete [<FONT COLOR=RED>Impossible</FONT> ]' );
	debug( 'Execution de la requete dans affichesujet [<FONT COLOR=RED>OK</FONT> ]<BR>' );
	$nb_resultat = mysql_num_rows($resultat);
	$i = $nb_resultat;
	
	while( $i > 0 )
	{
		$ligne	= mysql_fetch_array($resultat);
		$date	= reformatedate($ligne["date"]);
		$sujet	= $ligne["sujet"];
		printf("<font size=-1><b>%s <FONT COLOR=#009999>%s</b></font></font><br>\n", $date, $sujet);
		$i--;
	}
	mysql_close();
}

function affichenews($site, $base, $table) {
	connect();
	$requete = "select * from ".$table." where site='".$site."' order by id desc";
	$resultat = mysql_db_query($base, $requete)
	or die( 'affichenews: Execution de la requete [<FONT COLOR=RED>Impossible</FONT> ]' );
	debug( 'Execution de la requete dans affichenews [<FONT COLOR=RED>OK</FONT> ]<BR>' );
	$nb_resultat = mysql_num_rows($resultat);
	$i = $nb_resultat;

	while( $i > 0 )
	{
		$ligne	= mysql_fetch_array($resultat);
		list( $from, $e_mail )	= split( "<", $ligne["de"] );
		$date	= reformatedate($ligne["date"])." (".$ligne["date"].")";
		$date	= reformatedate($ligne["date"]);
		$msg	= htmlspecialchars( $ligne["message"] );
		$sujet	= $ligne["sujet"];
		if($ligne["id_img"]<>0) {
			printf("<TR><TD COLSPAN=2>\n<b>%s %s</b>\n</TD></TR>\n", $date, $sujet);
			printf("<TR><TD WIDTH=120>\n<A HREF=\"#\" ONCLICK=\"javascript:plopimg('getphoto_t.phtml?id=%d','#%d');\"><img src=\"gettn_t.phtml?id=%d\" border=0></a>\n</TD>\n", $ligne["id_img"], $ligne["id_img"], $ligne["id_img"]);
			printf("<TD VALIGN=bottom>\n%s\n<br><div align=right><font size=-2>(%s)</font></div>\n</TD></TR>", $msg, $from);
		} else {
			printf("<TR><TD COLSPAN=2>\n<b>%s %s</b>\n</TD></TR>\n", $date, $sujet);
			printf("<TR><TD COLSPAN=2>\n%s\n<br><div align=right><font size=-2>(%s)</font></div>\n</TD></TR>", $msg, $from);
		}
		$i--;
	}
	mysql_close();
}


?>
