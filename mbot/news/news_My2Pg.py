#!/usr/bin/env python

# $Id$

import Image, os, re, sys, getopt
import MySQLdb, pg
import ConfigParser

# Configuration file default location
CONFIG_FILE = "../mbot.conf"
# Table photo
photo_table     = "photo"
photo_seq_table = photo_table + "_id_seq"
# Table news
news_table      = "news"
news_seq_table  = news_table + "_id_seq"

def usage():
        """ print out the command usage """
        command = os.path.basename(sys.argv[0])
        print "%s [-c <config_file>]" % command

def migrate_photo(id):
    global DB, HOST, DB_USER, DB_PASS, photo_table, photo_seq_table

    # Connect to MySQL
    dbmy   = MySQLdb.connect(db=DB, host=HOST, user=DB_USER, passwd=DB_PASS)
    mycur  = dbmy.cursor()
    mycur.execute("select description, img_data, tnimg_data, filename, filesize, filetype from %s where id='%d'" % (photo_table, id))
    # Fetch data
    desc, Fdata, TNdata, Fname, Fsize, Ftype =  mycur.fetchone()
    print "Transfering %s (Name: %s - Size: %s - Type: %s)" % (desc, Fname, Fsize, Ftype)
    # Close MySQL connexion
    dbmy.close()
    # Connect to PostgreSQL
    dbpg   = pg.connect(dbname=DB, host=HOST, user=DB_USER, passwd=DB_PASS)
    # Copy images to PostgreSQL
    dbpg.query("begin")
    Olo    = dbpg.locreate(pg.INV_WRITE)
    TNlo   = dbpg.locreate(pg.INV_WRITE)
    # Insert data
    req    = dbpg.query("insert into %s (description, img_data, tnimg_data, filename, filesize, filetype) values ('%s', '%s', '%s', '%s', '%s', '%s')" % (photo_table, desc, Olo.oid, TNlo.oid, Fname, Fsize, Ftype))
    # Write data to Large Object
    Olo.open(pg.INV_WRITE)
    Olo.write(Fdata)
    Olo.close()
    TNlo.open(pg.INV_WRITE)
    TNlo.write(TNdata)
    TNlo.close()
    # Commit changes
    dbpg.query("commit")
    last_id = dbpg.query("select currval('%s')" % photo_seq_table).getresult()[0][0]
    print "%s transfered with id #%d" % (Fname, last_id)
    # Close PostgreSQL connexion
    dbpg.close()

    return last_id

def main():
	global CONFIG_FILE, photo_table, photo_seq_table, news_table, news_seq_table

	config_file = CONFIG_FILE
	try:
	   opts, args = getopt.getopt(sys.argv[1:], "c:")
	except getopt.GetoptError:
	   # print help information and exit:
	   usage()
	   sys.exit(2)

	for o, a in opts:
	   if o == "-c":
	      config_file = a

	config = ConfigParser.ConfigParser()
	config.read(configfile)

	# Reading news options
	photo_table     = config.get('NEWS','photo_tbl')
	photo_seq_table = config.get('NEWS','photo_tblsq')
	news_table      = config.get('NEWS','news_tbl')
	news_seq_table  = config.get('NEWS','news_tblsq')
	DB              = config.get('NEWS','db')
	DB_USER         = config.get('NEWS','db_user')
	DB_PASS         = config.get('NEWS','db_pass')
	HOST            = config.get('NEWS','host')

	# Connect to MySQL
	dbmy	= MySQLdb.connect(db=DB, host=HOST, user=DB_USER, passwd=DB_PASS)
	# Create cursor to execute queries
	mycur	= dbmy.cursor()
	mycur.execute("select site, date, de, sujet, message, id_img from %s" % news_table)
	count	= dbmy.affected_rows()
	print "Getting %d news" % count

	i = 0
	while i < count:
	    # Fetch news data
	    site, date, de, sujet, message, id_img =  mycur.fetchone()
	    # Connect to PostgreSQL
	    dbpg = pg.connect(dbname=DB, host=HOST, user=DB_USER, passwd=DB_PASS)
	    if id_img != 0:
	       image_id = migrate_photo(id_img)
	    else:
	       image_id = id_img
	    req  = dbpg.query("insert into %s (site, date, de, sujet, message, id_img) values ('%s', '%s', '%s', '%s', '%s', '%d')" % (news_table, site, date, de, re.escape(sujet), re.escape(message), image_id))
	    news_id = dbpg.query("select currval('%s')" % news_seq_table).getresult()[0][0]
	    dbpg.close()
	    print "News \"%s\" transfered with id #%d" % (sujet, news_id)
	    i = i +1

	dbmy.close()

if __name__ == "__main__":
	main()
