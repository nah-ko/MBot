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

# This class does not provides SGBD specific code, see MyNewsHandler
# and PgNewsHandler
class NewsHandler(MailHandler.MailHandler):
    """ Manage adding news in a data base """

    def read_conf(self, ConfObj):
        ''' Getting config options for this handler '''
        self.log.notice("[NewsHandler]: read_conf")
        self.read_conf2(ConfObj,
                       ['host', 'db', 'db_user', 'db_pass',
                        'photo_tbl', 'photo_tblsq',
                        'news_tbl', 'news_tblsq',
                        'site', 'attach_path', 'tnx', 'tny'])

    def getsite(self, e_mail):
        """ Get the site information """
        
        self.log.notice("[NewsHandler]: getsite")
        befat, aftat = e_mail.split('@')

        if len(aftat.split('>')) != 1:
                dom, B = aftat.split('>')
        elif len(aftat.split('>')) == 1:
            A = aftat.split('>')
            dom = A[0]
            
        self.log.debug("[NewsHandler]: getsite -> dom='%s'" % dom)

        try:
           dico_site = eval(self.site)
           site      = dico_site[dom]
        except KeyError, SyntaxError:
           site = 'test'

        self.log.debug("[NewsHandler]: getsite -> site='%s'" % site)
        return site
        
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

    def handle(self, body):
        "Get news from text and attachment if present"

        self.log.notice("[NewsHandler]")
        result    = "Automatic response to: " + self.params + "\n"
        id_img = id_news = 0

        # Handle text part of a news
        self.log.notice("[NewsHandler]: Use [%s] section" % self.section)
        if type(body) == type(""):
            id_news = self.add_news(body)
            result    = result + " #%d added" % id_news
            self.log.debug("[NewsHandler]: result='%s' for '%s'" \
                           % (result, self.section))

        # Handle image part of a news
        else:
            # This part is not image but html
            if type(body) == type(""):
                self.log.debug("[NewsHandler]: text part")
                if id_img != 0:
                    id_news = self.add_news(body, id_img)
                else:
                    id_news = self.add_news(body)

            # This part is not a text one
            else:
                maintype, subtype = body.get_content_type().split('/',1)
                self.log.debug("[NewsHandler]: maintype='%s'" \
                               % maintype + \
                               " subtype='%s'" \
                               % subtype)

                # We insert an image in the data base
                if maintype == "image":
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
                    img.thumbnail((int(self.tnX), int(self.tnY)))
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
                                   % (file, TNfile) + \
                                   "removed")
                    
                    result    = result + "Image #%d added" % id_img

        return [('text/plain', result)]
