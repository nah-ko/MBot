#!/usr/bin/env python

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

# $Id$

import MailHandler
import sys, os, email
import MySQLdb, re, Image

HOST	= "localhost"
DB 	= "db"
DB_USER = "user"
DB_PASS = "pass"

ATTACH_PATH = "/tmp/"
tnX	= 120
tnY	= 90

class NewsHandler(MailHandler.MailHandler):

	def add_img(self, filename, filetype, filedata, TNfiledata, filesize):
		db = MySQLdb.connect(db=DB, host=HOST, user=DB_USER, passwd=DB_PASS)
		news_id	= self.id
		TABLE	= "photo_test"
		desc	= "[News] " + filename
		myquery = "insert into %s (description,img_data,tnimg_data,filename,filesize,filetype) values ('%s','%s','%s','%s','%d','%s')" % (TABLE, desc, db.escape_string(filedata), db.escape_string(TNfiledata), filename, filesize, filetype)
		mycur	= db.cursor()
		mycur.execute(myquery)
		id	= db.insert_id()
		TABLE	= "news_test"
		myquery	= "update %s set id_img='%d' where id='%d'" % (TABLE, id, news_id)
		mycur   = db.cursor()
		mycur.execute(myquery)
		db.close()
		return id
	
	def domext(self,e_mail):
		befat, aftat = e_mail.split('@')

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
		TABLE 	= "news_test"
		if dest == "nah-ko.org":
			SITE	= "test"
		elif dest == "rein-team.darktech.org":
			SITE	= "reinteam"
		myquery = "insert into %s (site,date,de,message,id_img) values('%s','%s','%s','%s','%d')" % (TABLE, SITE, date, sender, re.escape(text), img_id)
		mycur	= db.cursor()
		mycur.execute(myquery)
		self.id	= db.insert_id()
		db.close()
		return self.id

	def handle(self, body):
		"Get news from text and attachment if present"

		id_img = id_news = 0
		if type(body) == type(""):
			id_news = self.add_news(body)
		else:
			if type(body) == type(""):
				if id_img != 0:
					id_news = self.add_news(body, id_img)
				else:
					id_news = self.add_news(body)
			else:
				maintype, subtype = body.get_content_type().split('/',1)
				if maintype == "image":
					file	= ATTACH_PATH + body.get_filename()
					TNfile	= ATTACH_PATH + "TN_" + body.get_filename()
					f	= open(file, "w")
					f.write(body.get_payload(decode=1))
					f.close()
					img	= Image.open(file)
					format	= img.format
				        img.thumbnail((tnX,tnY))
				        img.save(TNfile,format)         
				        f	= open(TNfile, "r")
				        TNdata  = f.read()   
				        f.close()            
					filesize = os.stat(file).st_size
					id_img	= self.add_img(body.get_filename(), body.get_content_type(), body.get_payload(decode=1), TNdata, filesize)
					os.remove(file)
					os.remove(TNfile)

		result	= "Automatic response:\n"
		result	= result + "News #%d added with image #%d (0 for none)" % (id_news, id_img)
		return [('text/plain', result)]
