#!/usr/bin/env python2.3

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

import MailHandler
import string, urllib, mimetools, urlparse

class UrlHandler(MailHandler.MailHandler):
    "Handle getting url given in mail"
    
    def handle(self, body):
        """ The body may contain one url per line """
        result = []

        for line in body.split():
            if line != '' and line is not None:
                (p, server, path, params, q, f) = urlparse.urlparse(line)
                url   = urlparse.urlunparse((p, server,
                                             urllib.quote(path),
                                             urllib.quote(params),
                                             urllib.quote(q, '/='),
                                             urllib.quote(f)))
                data  = urllib.urlopen(url)
                result.append((data.info().gettype(), data.read()))

        return result
            
