#!/usr/bin/env python2.3

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

# $Id$

import MailHandler
import string, urllib, httplib, mimetools
import ConfigParser

SECTION = "GOOGLE"

class GoogleHandler(MailHandler.MailHandler):
    "Handle getting url given in mail"
    
    def read_conf(self, ConfObj):
        ''' Getting config options for this handler '''

	self.HOST     = ConfObj.get(SECTION, 'host')
	self.BASE_URL = ConfObj.get(SECTION, 'base_url')

    def handle(self, body):
        """ The body may contain one url per line """
        result = []

        for line in body.split('\n'):
            if line != '' and line is not None:
                url = self.BASE_URL + urllib.quote(line)
                conn = httplib.HTTPConnection(self.HOST)
                conn.request("GET", url)
                r = conn.getresponse()

                type = r.msg.gettype()
                data = r.read()

                conn.close()
                
                result.append((type, data))

        return result
