#!/usr/bin/env python

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
# Author:  Christophe Truffier <toffe@nah-ko.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

# $Id$

import rfc822

class MailHandler:
    " To handle a mail, you'll have to inheritate from this class "
    def __init__(self, section, log, params,
                 dest="sended for", sender="sended by",
		 date="sended the", multipart_mesg="false"):
        self.section        = section
        self.log            = log
        self.params         = params
        self.date           = date
        self.sender         = sender
        self.dest           = dest
        self.multipart_mesg = multipart_mesg

    def read_conf(self, config, properties):
        ''' Config parser '''
	self.log.debug("[MailHandler]: read_conf2")
        for p in properties:
	    self.log.debug("[MailHandler]: p = %s" % p)
            if config.has_option(self.section, p):
                setattr(self, p, config.get(self.section, p))
            else:
                setattr(self, p, None)
    
    def handle(self, body):
        return [('text/plain', body)]

    def check_lists(self, config):
        """ Check if the user is authorized to use the handler """

	# Use email part of sender
        (name, sender) = rfc822.parseaddr(self.sender)
	self.log.debug("[check_lists]: sender = %s" % self.sender)
	self.log.debug("[check_lists]: sender(email) = %s" % sender)

        # First check black list
        if config.has_option(self.section, "BLACK_LIST"):
	    self.log.debug("[check_lists]: BLACK_LIST exists")
            BL = config.get(self.section, "BLACK_LIST")
	    self.log.debug("[check_lists]: BLACK_LIST=%s" % BL)
            if sender in BL:
                return False

        # Black list is not bloquing, check white list
        if config.has_option(self.section, "WHITE_LIST"):
	    self.log.debug("[check_lists]: WHITE_LIST exists")
            WL = config.get(self.section, "WHITE_LIST")
	    self.log.debug("[check_lists]: WHITE_LIST=%s" % WL)
            return sender in WL
        
        else:
            # If no white list is provided, mbot usage is accepted
            return True
