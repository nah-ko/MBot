#!/usr/bin/env python

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

# $Id$

import MailHandler
import sys,os,email
import MySQLdb

HOST	= "localhost"
DB 	= "mydbs"
DB_USER = "admin"
DB_PASS = "algonquin"

ATTACH_PATH = "/tmp/"

class NewsHandler(MailHandler.MailHandler):

	def add_img(self, filename, filetype, filedata, filesize):
		db = MySQLdb.connect(db=DB, host=HOST, user=DB_USER, passwd=DB_PASS)
		news_id	= self.id
		TABLE	= "bindat"
		desc	= "[News] " + filename
		myquery = "insert into %s (description,bin_data,filename,filesize,filetype) values ('%s','%s','%s','%d','%s')" % (TABLE, desc, db.escape_string(filedata), filename, filesize, filetype)
		mycur	= db.cursor()
		mycur.execute(myquery)
		id	= db.insert_id()
		TABLE	= "news"
		myquery	= "update %s set id_img='%d' where id='%d'" % (TABLE, id, news_id)
		mycur   = db.cursor()
		mycur.execute(myquery)
		db.close()
		return id
	
	def domext(self,email):
		befat, aftat = email.split('@')

		if len(aftat.split('>')) != 1:
		        dom, B = aftat.split('>')
		elif len(aftat.split('>')) == 1:
			A = aftat.split('>')
			dom = A[0]
		return dom

	def add_news(self, text, img_id=0):
		db 	= MySQLdb.connect(db=DB, host=HOST, user=DB_USER, passwd=DB_PASS)
		date 	= self.date
		sender 	= self.sender
		dest 	= self.domext(self.dest)
		TABLE 	= "news"
		if dest == "nah-ko.org":
			SITE	= "test"
		elif dest == "rein-team.darktech.org":
			SITE	= "reinteam"
		myquery = "insert into %s (site,date,de,message,id_img) values('%s','%s','%s','%s','%d')" % (TABLE, SITE, date, sender, text, img_id)
		mycur	= db.cursor()
		mycur.execute(myquery)
		self.id	= db.insert_id()
		db.close()
		return self.id

	def handle(self, body):
		"Get news from text and attachment if present"

		id_img = id_news = 0
		for part in body:
			if type(part) != type(""):
				maintype, subtype = part.get_content_type().split('/',1)
				if maintype == "image":
					file = ATTACH_PATH + part.get_filename()
					f = open(file, "w")
					f.write(part.get_payload(decode=1))
					f.close()
					filesize = os.stat(file).st_size
					id_img = self.add_img(part.get_filename(), part.get_content_type(), part.get_payload(decode=1), filesize)
			elif type(part) == type(""):
				if id_img != 0:
					id_news = self.add_news(part, id_img)
				else:
					id_news = self.add_news(part)
		result	= "Automatic response:\n"
		result	= result + "News #%d added with image #%d (0 for none)" % (id_news, id_img)
		return [('text/plain', result)]
