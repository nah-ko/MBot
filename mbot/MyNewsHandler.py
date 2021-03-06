#!/usr/bin/env python

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
# Author:  Christophe Truffier <toffe@nah-ko.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

# $Id$

import NewsHandler
import sys, os, email, re
import ConfigParser

import MySQLdb

class MyNewsHandler(NewsHandler.NewsHandler):
    """ Manage adding news in a MySQL data base """

    def dbconn(self):
        """ Connect to the data base """

        self.log.notice("[MyNewsHandler]: dbconn")
        db = MySQLdb.connect(db=self.db, host=self.host,
                             user=self.db_user, passwd=self.db_pass)
        return db

    def execQuery(self, sql):
        """ Execute the given query """

	self.log.notice("[MyNewsHandler]: execQuery")
        db    = self.dbconn()
        mycur = db.cursor()
        mycur.execute(sql)
        self.id = self.getid(db, self.news_tblsq)
        db.close()

        return self.id
    
    def execReadQuery(self, sql):
        """ Execute the given query """

	self.log.notice("[MyNewsHandler]: execReadQuery")
        db    = self.dbconn()
        mycur = db.cursor()
        mycur.execute(sql)
	res   = list(mycur.fetchall())
        db.close()

        return res 
    
    def getid(self, conn, table=None):
        """ Get the next available news Id """

        self.log.notice("[MyNewsHandler]: getid")
        id = conn.insert_id()
        self.log.debug("[MyNewsHandler]: getid -> id='%d'" % id)

        return id
	
    def add_img(self, filename, filetype, filedata, TNfiledata, filesize):
        """ Add an image in the database """
        
        self.log.notice("[MyNewsHandler]: add_img")
        news_id	= self.id
        desc	= "[News] " + filename

        myquery = """
        INSERT INTO %s (description, img_data, tnimg_data,
                        filename, filesize, filetype)
         VALUES ('%s','%s','%s','%s','%d','%s')
         """ % (self.photo_tbl, desc, db.escape_string(filedata),
                db.escape_string(TNfiledata), filename, filesize, filetype)

        # First insert the image
        db      = self.dbconn()
        mycur	= db.cursor()
        mycur.execute(myquery)

        # Now we add the link to the image from the news table
        id      = self.getid(db, self.photo_tblsq)
        self.log.debug("[MyNewsHandler]: add_img => id='%d'" % id)
        myquery	= "UPDATE %s SET id_img='%d' WHERE id='%d'" \
                  % (self.news_tbl, id, news_id)
        mycur	= db.cursor()
        mycur.execute(myquery)
        
        db.close()
        return id
    
