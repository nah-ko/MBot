#!/usr/bin/env python

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

from MailHandler import MailHandler

class GoogleHandler(MailHandler):
    "Handle getting url given in mail"
    
    def read_conf(self, ConfObj):
        ''' Getting config options for this handler '''
        self.log.notice("[GoogleHandler]: read_conf")
        MailHandler.read_conf(self, ConfObj,
	                      ['host', 'base_url'])

    def handle(self, body):
        """ The body may contain one url per line """
        result = []

        self.log.notice("[GoogleHandler]")
        for line in body.split('\n'):
            if line != '' and line is not None:
                url = self.base_url + urllib.quote(line)
                self.log.debug("[GoogleHandler]: url='%s'" \
                                   % url)
                conn = httplib.HTTPConnection(self.host)
                conn.request("GET", url)
                r = conn.getresponse()

                type = r.msg.gettype()
                data = r.read()

                conn.close()
                
                result.append((type, data))

        return result
