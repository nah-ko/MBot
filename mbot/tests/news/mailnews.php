<HTML>
<!--
$Id$

PHP script for mbot NewsHandler
Author: Christophe Truffier <toffe@nah-ko.org>

Useful if you want to display quickly datas on your website.
-->
<HEAD>
<TITLE>Mail News</TITLE>
<META NAME="Author" CONTENT="Toffe">
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">
<script LANGUAGE="JavaScript" SRC="/popuplib.js"></script>
</HEAD>
<BODY>
<center>
<h1> Mail News </h1>
<?
$debug = false;
require ($_SERVER["DOCUMENT_ROOT"]."/mailnews.inc");
?>
<h6> reception de news par mail<br>
 (page de test - Site: <? echo $site; ?>) </h6>
</center>
<?  affichesujet($site, $base, $table); ?>
<HR WIDTH=25>
<center>
<TABLE BORDER=0 width="50%">
<?  affichenews($site, $base, $table); ?>
</TABLE>
</BODY>
</HTML>
