<?

/*
Original PHP script by Florian Dittmer <dittmer@gmx.net>
Example php script to demonstrate the direct passing of binary data
to the user. More infos at http://www.phpbuilder.com
Syntax: gettn.phtml?id=<id>

$Id$

Modified for mbot NewsHandler by Christophe Truffier <toffe@nah-ko.org>
This script show thumbnail.
*/

if($id) {

    // you may have to modify login information for your database server:
    require($_SERVER["DOCUMENT_ROOT"].'/SQL.inc');
    MYSQL_CONNECT($serveur_SQL, $user, $user_pass);
    mysql_select_db("db");

    $query = "select tnimg_data,filetype from photo_test where id=$id";
    $result = @MYSQL_QUERY($query);

    $data = @MYSQL_RESULT($result,0,"tnimg_data");
    $type = @MYSQL_RESULT($result,0,"filetype");

    Header( "Content-type: $type");
    echo $data;

};
?>
