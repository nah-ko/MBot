#!/usr/bin/env python2.3

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html
#
# To install that mail bot, just add a line in your mail alias file:
#  mbot: "|/home/fontaine/dev/mbot/mbot.py"
#
# If you use exim, be sure to add the option 'pipe_as_creator' to your
# configuration, in the 'address_pipe' section

# $Id$

import sys, os, email, smtplib

# All this will be used to create the response mail
from email import Encoders
from email.MIMEAudio import MIMEAudio
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText

import MailHandler, UrlHandler, GoogleHandler

DEBUG        = False
LOGFILE      = "/tmp/mbot.log"
MBOT_ADDRESS = "mbot@localhost"

def read_email():
    str = sys.stdin.read()
    mesg = email.message_from_string(str)

    return mesg

if __name__ == "__main__":
    logfile = open(LOGFILE, 'a')

    mesg = read_email()

    sender  = mesg.get('From')
    subject = mesg.get('Subject')
    mesg_id = mesg.get('Message-Id')
    body    = mesg.get_payload()

    logfile.write("message: %s %s %s \n" % (mesg_id, sender, subject))

    resp = MIMEMultipart()
    resp['Subject']     =  'Re: %s' % subject
    resp['To']          = sender
    resp['In-Reply-To'] =  mesg_id

    if subject == 'wget':
        h = UrlHandler.UrlHandler()
    elif subject == 'google':
        h = GoogleHandler.GoogleHandler()
    else:
        h = MailHandler.MailHandler()

    if DEBUG:
        [(type, part)] = h.handle(body)
        print part
        sys.exit(0)

    for (type, part) in h.handle(body):
        maintype, subtype = type.split('/', 1)
        if maintype == 'text':
            data = MIMEText(part, _subtype=subtype)

        elif maintype == 'image':
            data = MIMEImage(part, _subtype=subtype)

        elif maintype == 'audio':
            data = MIMEAudio(part, _subtype=subtype)

        else:
            data = MIMEBase(maintype, subtype)
            data.set_payload(part)
            Encoders.encode_base64(msg)

        resp.attach(data)

    # Then we send the mail
    s = smtplib.SMTP()
    s.connect()
    s.sendmail(MBOT_ADDRESS, sender, resp.as_string())
    s.close()
