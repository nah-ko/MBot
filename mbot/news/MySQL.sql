# Test tables for MySQL
# You will need to create a database before !!
# $Id$

CREATE TABLE photo_test (
  id int(4) NOT NULL auto_increment,
  description varchar(50) default NULL,
  img_data longblob,
  tnimg_data longblob,
  filename varchar(50) default NULL,
  filesize varchar(50) default NULL,
  filetype varchar(50) default NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

CREATE TABLE news_test (
  id int(100) unsigned NOT NULL auto_increment,
  site text,
  date datetime,
  de text,
  sujet text,
  message text,
  id_img int(4) NOT NULL default '0',
  PRIMARY KEY  (id),
  KEY id (id)
) TYPE=MyISAM;

