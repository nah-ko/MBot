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
import ConfigParser

SECTION    = 'NEWS'

# This class does not provides SGBD specific code, see MyNewsHandler
# and PgNewsHandler
class NewsHandler(MailHandler.MailHandler):
    """ Manage adding news in a data base """

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
           dico_site = eval(self.SITE)
           site      = dico_site[dom]
        except KeyError, SyntaxError:
           site = 'test'

        self.log.debug("[NewsHandler]: getsite -> site='%s'" % site)
        return site
        
    def add_news(self, text, img_id=0):
        self.log.notice("[NewsHandler]: add_news")
        date     = self.date
        sender     = self.sender
        subject    = re.escape(self.params)
        SITE     = self.getsite(self.dest)
        
        if img_id == 0:
            myquery = """
            INSERT INTO %s (site,date,de,sujet,message)
            VALUES ('%s','%s','%s','%s','%s')
            """ % (self.NEWS_TBL, SITE, date, sender, subject, re.escape(text))
            
        else:
            myquery = """
            INSERT INTO %s (site,date,de,sujet,message,id_img)
            VALUES ('%s','%s','%s','%s','%s','%d')
            """ % (self.NEWS_TBL, SITE,
                   date, sender, subject, re.escape(text), img_id)
            
        self.execQuery(myquery)
        self.id    = self.getid(db, self.NEWS_TBLSQ)
        self.log.debug("[NewsHandler]: add_news -> id='%d'" % self.id)
        return self.id

    def read_conf(self, ConfObj):
        ''' Getting config options for this handler '''

        self.log.notice("[NewsHandler]: read_conf")
        self.HOST        = ConfObj.get(SECTION,'host')
        self.DB          = ConfObj.get(SECTION,'db')
        self.DB_USER     = ConfObj.get(SECTION,'db_user')
        self.DB_PASS     = ConfObj.get(SECTION,'db_pass')
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

        self.log.notice("[NewsHandler]")
        result    = "Automatic response to: " + self.params + "\n"
        id_img = id_news = 0

        # Handle text part of a news
        if type(body) == type(""):
            id_news = self.add_news(body)
            result    = result + "News #%d added" % id_news
            self.log.debug("[NewsHandler]: result='%s' for '%s'" \
                           % (result, self.params))

        # Handle image part of a news
        else:
            # This seems suspect
            if type(body) == type(""):
                self.log.debug("[NewsHandler]: text part")
                if id_img != 0:
                    id_news = self.add_news(body, id_img)
                else:
                    id_news = self.add_news(body)

            # This part is not a text one
            else:
                maintype, subtype = body.get_content_type().split('/',1)

                # We insert an image in the data base
                if maintype == "image":
                    self.log.debug("[NewsHandler]: image part")
                    
                    file    = self.ATTACH_PATH + body.get_filename()
                    TNfile  = self.ATTACH_PATH + "TN_" + body.get_filename()

                    # We first save the image
                    f = open(file, "w")
                    f.write(body.get_payload(decode=1))
                    f.close()
                    
                    self.log.debug("[NewsHandler]: image saved to '%s'" \
                                   % self.ATTACH_PATH)

                    # Then a thumbnail
                    img    = Image.open(file)
                    img.thumbnail((int(self.tnX), int(self.tnY)))
                    img.save(TNfile, img.format)         
                    f    = open(TNfile, "r")
                    TNdata  = f.read()   
                    f.close()
                    
                    self.log.debug("[NewsHandler]: thumbnail created to '%s'" \
                                   % self.ATTACH_PATH)
                    
                    filesize = os.stat(file).st_size

                    # Now we add the images in the data base
                    id_img   = self.add_img(body.get_filename(),
                                            body.get_content_type(),
                                            body.get_payload(decode=1),
                                            TNdata, filesize)
                    
                    self.log.debug("[NewsHandler]: image #%d " % id_img + \
                                   "added to DB '%s'" % self.DB)

                    # And we clean the temporary created files
                    os.remove(file)
                    os.remove(TNfile)
                    
                    self.log.debug("[NewsHandler]: '%s' and '%s' " \
                                   % (file, TNfile) + \
                                   "removed")
                    
                    result    = result + "Image #%d added" % id_img

        return [('text/plain', result)]
