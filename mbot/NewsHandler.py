#!/usr/bin/env python

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
# Author:  Christophe Truffier <toffe@nah-ko.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

# $Id$

import MailHandler
import sys, os, email
import re, Image
import MySQLdb, pg
import ConfigParser

from pg import INV_WRITE

SECTION	= 'NEWS'

class NewsHandler(MailHandler.MailHandler):

	def add_img(self, filename, filetype, filedata, TNfiledata, filesize):
		if self.DB_TYPE == 'mysql':
			db = MySQLdb.connect(db=self.DB, host=self.HOST, user=self.DB_USER, passwd=self.DB_PASS)
		elif self.DB_TYPE == 'postgresql':
			db = pg.connect(dbname=self.DB, host=self.HOST, user=self.DB_USER, passwd=self.DB_PASS)
		news_id	= self.id
		desc	= "[News] " + filename
		if self.DB_TYPE == 'mysql':
			myquery = "insert into %s (description,img_data,tnimg_data,filename,filesize,filetype) values ('%s','%s','%s','%s','%d','%s')" % (self.PHOTO_TBL, desc, db.escape_string(filedata), db.escape_string(TNfiledata), filename, filesize, filetype)
			mycur	= db.cursor()
			mycur.execute(myquery)
		elif self.DB_TYPE == 'postgresql':
			db.query("begin")
			img_LO   = db.locreate(INV_WRITE)
			TNimg_LO = db.locreate(INV_WRITE)
			req      = db.query("insert into %s (description,img_data,tnimg_data,filename,filesize,filetype) values ('%s','%s','%s','%s','%d','%s')" % (self.PHOTO_TBL, desc, img_LO.oid, TNimg_LO.oid, filename, filesize, filetype))
			img_LO.open(INV_WRITE)
			img_LO.write(filedata)
			img_LO.close()
			TNimg_LO.open(INV_WRITE)
			TNimg_LO.write(TNfiledata)
			TNimg_LO.close()
			db.query("commit")
		id      = self.getid(db, self.PHOTO_TBLSQ)
		myquery	= "update %s set id_img='%d' where id='%d'" % (self.NEWS_TBL, id, news_id)
		if self.DB_TYPE == 'mysql':
			mycur	= db.cursor()
			mycur.execute(myquery)
		elif self.DB_TYPE == 'postgresql':
			req     = db.query(myquery)
		db.close()
		return id
	
	def getsite(self,e_mail):
		befat, aftat = e_mail.split('@')

		if len(aftat.split('>')) != 1:
		        dom, B = aftat.split('>')
		elif len(aftat.split('>')) == 1:
			A = aftat.split('>')
			dom = A[0]
		try:
		   dico_site = eval(self.SITE)
		   site      = dico_site[dom]
		except KeyError, SyntaxError:
		   site = 'test'

		return site

	def getid(self, conn, table=None):
		if self.DB_TYPE == 'mysql':
			id = conn.insert_id()
		elif self.DB_TYPE == 'postgresql':
			id = conn.query("select currval('%s')" % table).getresult()[0][0]
			# getresult()[0][0] <-- nedded because query
			# result return a tuple which contains (value,?)
			# where «value» is the ID.

		return id
	
	def add_news(self, text, img_id=0):
		if self.DB_TYPE == 'mysql':
			db = MySQLdb.connect(db=self.DB, host=self.HOST, user=self.DB_USER, passwd=self.DB_PASS)
		elif self.DB_TYPE == 'postgresql':
			db = pg.connect(dbname=self.DB, host=self.HOST, user=self.DB_USER, passwd=self.DB_PASS)
		date 	= self.date
		sender 	= self.sender
		subject	= re.escape(self.params)
		SITE 	= self.getsite(self.dest)
		myquery = "insert into %s (site,date,de,sujet,message,id_img) values('%s','%s','%s','%s','%s','%d')" % (self.NEWS_TBL, SITE, date, sender, subject, re.escape(text), img_id)
		if self.DB_TYPE == 'mysql':
			mycur	= db.cursor()
			mycur.execute(myquery)
		elif self.DB_TYPE == 'postgresql':
			req     = db.query(myquery)
		self.id	= self.getid(db, self.NEWS_TBLSQ)
		db.close()
		return self.id

	def read_conf(self, ConfObj):
		''' Getting config options for this handler '''

		self.HOST        = ConfObj.get(SECTION,'host')
		self.DB          = ConfObj.get(SECTION,'db')
		self.DB_USER     = ConfObj.get(SECTION,'db_user')
		self.DB_PASS     = ConfObj.get(SECTION,'db_pass')
		self.DB_TYPE     = ConfObj.get(SECTION,'db_type')
		self.PHOTO_TBL   = ConfObj.get(SECTION,'photo_tbl')
		self.PHOTO_TBLSQ = ConfObj.get(SECTION,'photo_tblsq')
		self.NEWS_TBL    = ConfObj.get(SECTION,'news_tbl')
		self.NEWS_TBLSQ  = ConfObj.get(SECTION,'news_tblsq')
		self.SITE        = ConfObj.get(SECTION,'site')
		self.ATTACH_PATH = ConfObj.get(SECTION,'attach_path')
		self.tnX         = ConfObj.get(SECTION,'tnx')
		self.tnY         = ConfObj.get(SECTION,'tny')

	def handle(self, body):
		"Get news from text and attachment if present"

		result	= "Automatic response to: " + self.params + "\n"
		id_img = id_news = 0
		if type(body) == type(""):
			id_news = self.add_news(body)
			result	= result + "News #%d added" % id_news
		else:
			if type(body) == type(""):
				if id_img != 0:
					id_news = self.add_news(body, id_img)
				else:
					id_news = self.add_news(body)
			else:
				maintype, subtype = body.get_content_type().split('/',1)
				if maintype == "image":
					file	= self.ATTACH_PATH + body.get_filename()
					TNfile	= self.ATTACH_PATH + "TN_" + body.get_filename()
					f	= open(file, "w")
					f.write(body.get_payload(decode=1))
					f.close()
					img	= Image.open(file)
					format	= img.format
				        img.thumbnail((int(self.tnX),int(self.tnY)))
				        img.save(TNfile,format)         
				        f	= open(TNfile, "r")
				        TNdata  = f.read()   
				        f.close()            
					filesize = os.stat(file).st_size
					id_img	= self.add_img(body.get_filename(), body.get_content_type(), body.get_payload(decode=1), TNdata, filesize)
					os.remove(file)
					os.remove(TNfile)
					result	= result + "Image #%d added" % id_img

		return [('text/plain', result)]
