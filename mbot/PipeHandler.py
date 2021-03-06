#!/usr/bin/env python

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

# $Id$

import MailHandler
import string, popen2

class PipeHandler(MailHandler.MailHandler):
    "Handle passing mail body parts to arbitrary command"
    
    def handle(self, body):
        """ The body contains a input file """

        self.log.notice("[PipeHandler]")
        command = self.params
        self.log.debug("[PipeHandler]: command='%s'" % command)

        pout, pin = popen2.popen4(command)
        pin.write(body)
        pin.close()
        
        result = pout.read()
        pout.close()
        self.log.debug("[PipeHandler]: result='%s'" % result)
        
        return [('text/plain', result)]
            
