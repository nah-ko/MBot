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

from MailHandler import MailHandler

class UrlHandler(MailHandler):
    "Handle getting url given in mail"
    
    def read_conf(self, ConfObj):
        ''' Getting config options for this handler '''
        self.log.notice("[UrlHandler]: read_conf")
        MailHandler.read_conf(self, ConfObj,
	                      ['mailsize', 'attsize'])

    def handle(self, body):
        """ The body may contain one url per line """
        result    = []
        glob_size = 0

        self.log.notice("[UrlHandler]")
        for line in body.split():
            if glob_size < self.mailsize:
                if line != '' and line is not None:
                    (p, server, path, params, q, f) = urlparse.urlparse(line)
                    url   = urlparse.urlunparse((p, server,
                                                 urllib.quote(path),
                                                 urllib.quote(params),
                                                 urllib.quote(q, '/='),
                                                 urllib.quote(f)))
                    self.log.debug("[UrlHandler]: url='%s'" % url)

                    # Now we get the source and read infos
                    src  = urllib.urlopen(url)
                    size = int(src.info().getheader("Content-Length"))
                    self.log.debug("[UrlHandler]: size='%d'" % size)
                        
                    if size < self.attsize:
                        result.append((src.info().gettype(), src.read()))
                        glob_size += size
                                
                        self.log.debug(
                            "[UrlHandler]: glob_size='%d'" % glob_size)
                        self.log.notice(
                            "[UrlHandler]: Retreiving url '%s'" % url)
                    else:
                        type = "text/plain"
                        data = "Attachment size exceed %s (%d)" % (self.attsize,
                                                                   size) + \
                               " for '%s'" % url
                        self.log.notice("[UrlHandler]: %s" % data)
                        result.append((type, data))
            else:
                type = "text/plain"
                data = "Mail size exceed %s (%d)" % (self.mailsize,
                                                     glob_size)
                self.log.notice("[UrlHandler]: %s" % data)
                result.append((type, data))

        return result
            
