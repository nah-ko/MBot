#!/usr/bin/env python

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

# $Id$

import MailHandler
import sys,os,email,MySQLdb

HOST	= "localhost"
DB 	= "mydbs"
TABLE 	= "news"
DB_USER = "user"
DB_PASS = "pass"
SITE 	= "test"

ATTACH_PATH = "/tmp/"

class NewsHandler(MailHandler.MailHandler):

	def add_news(self, text):
		db = MySQLdb.connect(db=DB, host=HOST, user=DB_USER, passwd=DB_PASS)
		#query = "select * from news where site='test';"
		date = "Dimanche 22 Avril 2003"
		sender = "\"Christophe Truffier\" <ctruffier@cvf.fr>"
		query = "insert into " + TABLE + " values('','" + SITE + "','" + date + "','" + sender + "','" + text + "')"
		print query
		#insert into mailnews values('','$SITE','$DATE','$FROM','$BODY')
		db.close()

	def handle(self, body):
		"Get news from text and attachment if present"

		for part in body:
			if type(part) == type(""):
				#news = part
				self.add_news(part)
			else:
				maintype, subtype = part.get_content_type().split('/',1)
				if maintype == "image":
					file = ATTACH_PATH + part.get_filename()
					f = open(file, "w")
					f.write(part.get_payload())
					f.close()
