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
import sys, os, email, re, Image
import ConfigParser

from MailHandler import MailHandler

# This class does not provides SGBD specific code, see MyNewsHandler
# and PgNewsHandler
class NewsHandler(MailHandler):
    """ Manage adding news in a data base """

    def read_conf(self, ConfObj):
        ''' Getting config options for this handler '''
        self.log.notice("[NewsHandler]: read_conf")
        MailHandler.read_conf(self, ConfObj,
                       ['host', 'db', 'db_user', 'db_pass',
                        'photo_tbl', 'photo_tblsq',
                        'news_tbl', 'news_tblsq',
                        'site', 'attach_path', 'tnx', 'tny'])

    def getsite(self, e_mail):
        """ Get the site information """
        
	import rfc822

        self.log.notice("[NewsHandler]: getsite")
	(name, sender) = rfc822.parseaddr(e_mail)
        self.log.debug("[NewsHandler]: getsite -> sender='%s'" % sender)
        (user, dom)    = sender.split('@')
        self.log.debug("[NewsHandler]: getsite -> dom='%s'" % dom)

        try:
           dico_site = eval(self.site)
           site      = dico_site[dom]
        except KeyError, SyntaxError:
           site = 'test'

        self.log.debug("[NewsHandler]: getsite -> site='%s'" % site)
        return site

    def getlist(self):
	""" Get the whole entry list """

	self.log.notice("[NewsHandler]: getlist")
	myquery = """
	SELECT id, id_img, site, date, de, sujet FROM %s
	""" % self.news_tbl
	self.log.debug("[NewsHandler]: myquery = %s" % myquery)
	list = self.execReadQuery(myquery)
	text = "\tid\t|\tid_img\t|\tsite\t|\tdate\t|\tde\t|\tsujet\t\n"
	for (ID, ID_IMG, SITE, DATE, DE, SUJET) in list:
	    text = text + "\t%s\t|\t%s\t|\t%s\t|\t%s\t|\t%s\t|\t%s\n" % (ID,
		   ID_IMG, SITE, DATE, DE, SUJET)
	self.log.debug("[NewsHandler]: list = %s" % list)

	return text
        
    def add_news(self, text, img_id=0):
        self.log.notice("[NewsHandler]: add_news")
        date    = self.date
        sender  = self.sender
        subject = re.escape(self.params)
        SITE    = self.getsite(self.dest)
        
        if img_id == 0:
            myquery = """
            INSERT INTO %s (site,date,de,sujet,message)
            VALUES ('%s','%s','%s','%s','%s')
            """ % (self.news_tbl, SITE, date, sender, subject, re.escape(text))
            
        else:
            myquery = """
            INSERT INTO %s (site,date,de,sujet,message,id_img)
            VALUES ('%s','%s','%s','%s','%s','%d')
            """ % (self.news_tbl, SITE,
                   date, sender, subject, re.escape(text), img_id)
            
	self.log.debug("[NewsHandler]: myquery = %s" % myquery)
        self.id    = self.execQuery(myquery)
        self.log.debug("[NewsHandler]: add_news -> id='%d'" % self.id)
        return self.id


    # Decode text and insert it into our news data base
    #
    def handle_text_part(self, id_img, body):
        """insert the text part of the news"""

        self.log.debug("[NewsHandler]: text part")

        text = body.get_payload(decode=1)
            
        if id_img != 0:
            id_news = self.add_news(text, id_img)
        else:
            id_news = self.add_news(text)

        result = "Entry #%d added" % id_news
        
        self.log.debug("[NewsHandler]: result='%s' for '%s'" \
                       % (result, self.section))
                
        return id_news, result


    # Handle is called on each part of multipart mail, or on body of
    # message received
    #
    def handle(self, body):
        "Get news from text and attachment if present"

        self.log.notice("[NewsHandler]")
        result    = "Automatic response to: " + self.params + "\n"
        id_img = id_news = 0

        self.log.notice("[NewsHandler]: Use [%s] section" % self.section)

	# Just get data list and stop.
	import string

	if string.strip(self.params)[:7] == 'getlist':
	    self.log.debug("[NewsHandler]: found getlist buzzword")
	    result = result + self.getlist()

	else:
	    # Handle simple text messages
	    if not self.multipart_mesg:
		id_news, res = self.handle_text_part(id_img, body)
		result       = result + res
            
	    # Handle multipart messages
	    else:
		content_type      = body.get_content_type()
		maintype, subtype = content_type.split('/',1)

		self.log.debug("[NewsHandler]: maintype='%s'" % maintype +
			       " subtype='%s'" % subtype)

		# text parts are our news
		if maintype == "text":
		    if subtype == "plain":
			id_news, res = self.handle_text_part(id_img, body)
			result       = result + res
		    else:
			# We do not consider other text parts
			pass

		# other type parts, we care about 'image' ones
		elif maintype == "image":
		    # We insert an image in the data base
		    self.log.debug("[NewsHandler]: image part")
                    
		    file    = self.attach_path + body.get_filename()
		    TNfile  = self.attach_path + "TN_" + body.get_filename()
                
		    # We first save the image
		    f = open(file, "w")
		    f.write(body.get_payload(decode=1))
		    f.close()
                
		    self.log.debug("[NewsHandler]: image saved to '%s'" \
                               % self.attach_path)

		    # Then a thumbnail
		    img    = Image.open(file)
		    img.thumbnail((int(self.tnx), int(self.tny)))
		    img.save(TNfile, img.format)         
		    f    = open(TNfile, "r")
		    TNdata  = f.read()   
		    f.close()
                    
		    self.log.debug("[NewsHandler]: thumbnail created to '%s'" \
                               % self.attach_path)
                    
		    filesize = os.stat(file).st_size

		    # Now we add the images in the data base
		    id_img   = self.add_img(body.get_filename(),
                                        body.get_content_type(),
                                        body.get_payload(decode=1),
                                        TNdata, filesize)
                    
		    self.log.debug("[NewsHandler]: image #%d " % id_img + \
                               "added to DB '%s'" % self.db)

		    # And we clean the temporary created files
		    os.remove(file)
		    os.remove(TNfile)
                    
		    self.log.debug("[NewsHandler]: '%s' and '%s' " \
                               % (file, TNfile) + "removed")
                    
		    result = result + "Image #%d added" % id_img
                
		else:
		    # We do not consider other maintypes
		    pass

        return [('text/plain', result)]
