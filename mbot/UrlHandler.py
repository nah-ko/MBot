#!/usr/bin/env python

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

# $Id$

import MailHandler
import string, urllib, mimetools, urlparse

class UrlHandler(MailHandler.MailHandler):
    "Handle getting url given in mail"
    
    def handle(self, body):
        """ The body may contain one url per line """
        result = []
	size   = 0

        for line in body.split():
            if line != '' and line is not None:
                (p, server, path, params, q, f) = urlparse.urlparse(line)
                url   = urlparse.urlunparse((p, server,
                                             urllib.quote(path),
                                             urllib.quote(params),
                                             urllib.quote(q, '/='),
                                             urllib.quote(f)))
		size += urllib.urlopen(url).info().getheader("Content-Length")
		if size < self.ATTSIZE:
			data  = urllib.urlopen(url)
			result.append((data.info().gettype(), data.read()))
		else:
			type = "text/plain"
			data = "Attachment size exceed %s" % self.ATTSIZE
			result.append((type, data))

        return result
            
