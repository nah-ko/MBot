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
import sys, os, email
import ConfigParser

import pg
from pg import INV_WRITE

class PgNewsHandler(NewsHandler.NewsHandler):
    """ Manage adding news in a PostgreSQL data base """

    def dbconn(self):
        """ Connect to the data base """

        self.log.notice("[PgNewsHandler]: dbconn")
        db = pg.connect(dbname=self.db, host=self.host,
                        user=self.db_user, passwd=self.db_pass)

        return db

    def execQuery(self, sql):
        """ Execute the given query """

        self.log.notice("[PgNewsHandler]: execQuery")
        db      = self.dbconn()
        req     = db.query(sql)
        self.log.debug("[PgNewsHandler]: execQuery, req = %s" % req)
        self.id = self.getid(db, self.news_tblsq)
        db.close()

        return self.id

    def execReadQuery(self, sql):
        """ Execute the given query """

        self.log.notice("[PgNewsHandler]: execReadQuery")
        db      = self.dbconn()
        req     = db.query(sql).getresult()
        self.log.debug("[PgNewsHandler]: execReadQuery, req = %s" % req)
        db.close()

        return req

    def getid(self, conn, table=None):
        """ Get the next available news Id """

        self.log.notice("[PgNewsHandler]: getid")

        # result return a tuple which contains (value,?)  where
        # 'value' is the ID.
        # So we get the value with getresult()[0][0]
        id = conn.query("select currval('%s')" % table).getresult()[0][0]

        self.log.debug("[PgNewsHandler]: getid -> id='%d'" % id)
        return id

    def add_img(self, filename, filetype, filedata, TNfiledata, filesize):
        """ Add an image as a Large Object in the database """ 

        self.log.notice("[PgNewsHandler]: add_img")

        news_id	= self.id
        desc	= "[News] " + filename
        
        db      = self.dbconn()
        db.query("begin")

        # We create Large Object
        img_LO   = db.locreate(INV_WRITE)
        TNimg_LO = db.locreate(INV_WRITE)

        img_LO.open(INV_WRITE)
        img_LO.write(filedata)
        img_LO.close()
        
        TNimg_LO.open(INV_WRITE)
        TNimg_LO.write(TNfiledata)
        TNimg_LO.close()
        
        # The SQL query
        sql = """
        INSERT INTO %s (description, img_data, tnimg_data,
                        filename, filesize,filetype)
        VALUES ('%s','%s','%s','%s','%d','%s')
        """ % (self.photo_tbl, desc, img_LO.oid, TNimg_LO.oid,
               filename, filesize, filetype)
        req      = db.query(sql)

        db.query("commit")

        # Now we add the link to the image from the news table
        id      = self.getid(db, self.photo_tblsq)
        self.log.debug("[PgNewsHandler]: add_img => id='%d'" % id)
        myquery	= "UPDATE %s SET id_img='%d' WHERE id='%d'" \
                  % (self.news_tbl, id, news_id)
        
        req     = db.query(myquery)
        db.close()

        return id
	
