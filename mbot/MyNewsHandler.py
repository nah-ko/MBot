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
import sys, os, email, re, Image
import ConfigParser

import MySQLdb

SECTION	= 'NEWS'

class MyNewsHandler(NewsHandler.NewsHandler):
    """ Manage adding news in a MySQL data base """

    def dbconn(self):
        """ Connect to the data base """
        self.log.notice("[MyNewsHandler]: dbconn")
        db = MySQLdb.connect(db=self.DB, host=self.HOST,
                             user=self.DB_USER, passwd=self.DB_PASS)
        return db

    def execQuery(self, sql):
        """ Execute the given query """
        db    = self.dbconn()
        mycur = db.cursor()
        mycur.execute(sql)
        db.close()

        return self.id
    
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
         """ % (self.PHOTO_TBL, desc, db.escape_string(filedata),
                db.escape_string(TNfiledata), filename, filesize, filetype)

        # First insert the image
        db      = self.dbconn()
        mycur	= db.cursor()
        mycur.execute(myquery)
        self.log.debug("[MyNewsHandler]: add_img")

        # Now we add the link to the image from the news table
        id      = self.getid(db, self.PHOTO_TBLSQ)
        myquery	= "UPDATE %s SET id_img='%d' WHERE id='%d'" \
                  % (self.NEWS_TBL, id, news_id)
        mycur	= db.cursor()
        mycur.execute(myquery)
        
        db.close()
        return id
    
