#!/usr/bin/env python2.3

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

class MailHandler:
    " To handle a mail, you'll have to inheritate from this class "
    def handle(self, body):
        return [body]

