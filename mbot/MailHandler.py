#!/usr/bin/env python

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
# Author:  Christophe Truffier <toffe@nah-ko.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

# $Id$

class MailHandler:
    " To handle a mail, you'll have to inheritate from this class "
    def __init__(self, section, log, params,
                 dest="sended for", sender="sended by", date="sended the"):
        self.section = section
        self.log     = log
        self.params  = params
        self.date    = date
        self.sender  = sender
        self.dest    = dest

    def read_conf(self, config):
        ''' Config parser '''
        pass
    
    def read_conf(self, config, properties):
        ''' Config parser '''
        for p in properties:
            if config.has_option(self.section, p):
                setattr(self, p, config.get(self.section, p))
            else:
                setattr(self, p, None)

    
    def handle(self, body):
        return [('text/plain', body)]

    def check_lists(self, config):
        """ Check if the user is authorized to use the handler """

        # First check black list
        if config.has_option(self.section, "BLACK_LIST"):
            BL = config.get(self.section, "BLACK_LIST")
            if self.sender in BL:
                return False

        # Black list is not bloquing, check white list
        if config.has_option(self.section, "WHITE_LIST"):
            WL = config.get(self.section, "WHITE_LIST")
            return self.sender in WL
        
        else:
            # If no white list is provided, mbot usage is accepted
            return True
