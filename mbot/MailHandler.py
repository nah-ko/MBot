#!/usr/bin/env python

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
# Author:  Christophe Truffier <toffe@nah-ko.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

# $Id$

SECTION = ""

class MailHandler:
    " To handle a mail, you'll have to inheritate from this class "
    def __init__(self, log, params, dest="sended for", sender="sended by", date="sended the"):
        self.log    = log
        self.params = params
	self.date   = date
	self.sender = sender
	self.dest   = dest

    def read_conf(self, config):
	''' Config parser '''
    	pass
    
    def handle(self, body):
        return [('text/plain', body)]

