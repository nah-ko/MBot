#!/usr/bin/env python2.3

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

# $Id$

class MailHandler:
    " To handle a mail, you'll have to inheritate from this class "
    def __init__(self, params, dest="sended for", sender="sended by", date="sended the"):
        self.params = params
	self.date   = date
	self.sender = sender
	self.dest   = dest
    
    def handle(self, body):
        return [('text/plain', body)]

