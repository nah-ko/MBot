#!/usr/bin/env python

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
# Author:  Christophe Truffier <toffe@nah-ko.org>
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

import sys, os, getopt, email, smtplib, mimify
import ConfigParser, time, socket, rfc822

# All this will be used to create the response mail
from email import Encoders
from email.Utils import formatdate
from email.MIMEBase import MIMEBase
from email.MIMEAudio import MIMEAudio
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from mimify import mime_decode_header

import MailHandler
import Logger

# default values
global MBOT_ADDRESS, LOG_LEVEL

ProgPath     = os.path.dirname(os.path.realpath(sys.argv[0]))
CONFIG_FILE  = ProgPath + "/mbot.conf"
MBOT_ADDRESS = "mbot@localhost"
LOG_LEVEL    = "debug"
SECTIONS     = ""
RELEASE      = "0.2"

def read_defaults(configfile = CONFIG_FILE):
	''' Reading configuration file '''

	global MBOT_ADDRESS, LOG_LEVEL, SECTIONS
	
	SECTION = 'DEFAULT'

	# Opening file
	config = ConfigParser.ConfigParser()
	config.read(configfile)
	
	# Reading options
	if config.has_option(SECTION, 'MBOT_ADDRESS'):
	    MBOT_ADDRESS = config.get(SECTION, 'MBOT_ADDRESS')
	if config.has_option(SECTION, 'log_level'):
	    LOG_LEVEL    = config.get(SECTION, 'log_level')
	# Look for section list
	SECTIONS = config.sections()

	return config

def read_email():
	''' Reading a mail message '''
	str = sys.stdin.read()
	mesg = email.message_from_string(str)

	return mesg

def attach(mesg, response):
	""" attach a handler response to our return mail"""
	global log

	(type, out) = response
	maintype, subtype = type.split('/', 1)
	log.debug("%s part type" % maintype)
	
	if maintype == 'text':
		data = MIMEText(out, _subtype=subtype)
		log.debug("Result is:\n%s" % out)
		
	elif maintype == 'image':
		data = MIMEImage(out, _subtype=subtype)
		
	elif maintype == 'audio':
		data = MIMEAudio(out, _subtype=subtype)
		
	else:
		# Generic mime encoding
		data = MIMEBase(maintype, subtype)
		data.set_payload(out)
		Encoders.encode_base64(data)
		
	mesg.attach(data)

	

def main():
	""" Here we do the job """
	global RELEASE, MBOT_ADDRESS, CONFIG_FILE, LOG_LEVEL, log

	from optparse import OptionParser

	# Define usage and give command line options to parser object
	Usage  = "usage: %prog [options]"
	Ver    = "%prog " + RELEASE
	Parser = OptionParser(usage = Usage, version = Ver)
	Parser.add_option("-c", "--configfile", action="store", type="string",
	                  dest="ConfFile", metavar="FILE",
			  default=CONFIG_FILE,
			  help="Configuration file location")
	(options, args) = Parser.parse_args()
	confErrMsg      = ""

	if os.path.exists(options.ConfFile):
	    config_file = options.ConfFile
	else:
	    confErrMsg  = "Sorry, %s file doesn't exists using " \
	                  "default one instead" % options.ConfFile
	    config_file = CONFIG_FILE

	Conf = read_defaults(config_file)
	log  = Logger.Logger(LOG_LEVEL)
	
	if confErrMsg != "":
	    log.err(confErrMsg)
	log.notice("Using config file %s\n" % config_file)
	log.debug("Configuration values: MBOT_ADDRESS='%s'" \
		      % MBOT_ADDRESS + \
		      "LOG_LEVEL='%s'" \
		      % LOG_LEVEL)

	# we read the mail
	mesg = read_email()

	sender  = mesg.get('From')
	subject = mime_decode_header(mesg.get('Subject'))
	mesg_id = mesg.get('Message-Id')
	date    = time.strftime('%Y-%m-%d %H:%M:%S',
				rfc822.parsedate(mesg.get('Date')))
	dest    = mesg.get('To')
	
	log.notice("Incoming mail: the %s, from '%s' [%s] to '%s' " \
		   % (date, sender, mesg_id, dest) + \
		   "with subject '%s'" % subject)

	log.notice("message: %s %s %s \n" % (mesg_id, sender, subject))

	# we prepare the response
	resp = MIMEMultipart()
	resp['Subject']     = 'Re: %s' % subject
	resp['To']          = sender
	resp['In-Reply-To'] = mesg_id
	resp['Date']        = formatdate(time.mktime(time.localtime()), True)
	resp['From']        = dest

	# we initialize a handler corresponding to the given subject
	# first we create a dict hs which associate handler with subject
	# hs = {subject: [section, handler], ...}
	hs = {}
	for section in SECTIONS:
		log.debug("section: %s" % section)
		subjects = section.split(',')
		handler  = Conf.get(section, 'handler')
		log.debug("subjects: %s for handler: %s" % (subjects,
                                                            handler))
		for s in subjects:
			hs[s] = [section, handler]
			log.debug("subject: %s" % s)
	log.debug("Modules by subject: %s" % hs)

	# now we can try to import appropriate module and use it
	h = None
	for s in hs:
		if subject.find(s) == 0:
			section = hs[s][0]
			handler = hs[s][1]
			log.debug("using handler: %s" % handler)
			try:
				handlerModule = __import__(handler)
				log.notice("Using handler: %s" % handler)

				handlerClass = getattr(handlerModule, handler)
				log.debug("handlerClass: %s" % handlerClass)

				h = handlerClass(section, log,
						 subject[len(s):],
						 dest, sender, date,
						 mesg.is_multipart())
				
				log.debug("Instanciate handler %s for '%s'" \
					  % (handler, subject[len(s):]))
			except:
				log.err("Impossible to load handler: %s" \
					  % handler)
				log.err("%s: %s" \
					  % (sys.exc_type, sys.exc_value))
			break

	# If we have no handler, we send an error mail
	if h is None:
		log.err("No handler found for '%s'" % subject)
		mesg = "Sorry, mbot is not configured to handle your request"
		resp.attach(MIMEText(mesg))

	# Check if user is authorized to use mbot handler
	elif not h.check_lists(Conf):
		log.err("%s is not allowed to use mbot handler '%s'" \
			% (sender, handler))
		mesg = "Sorry, mbot is not allowed to handle your request"
		resp.attach(MIMEText(mesg))

	# Here we apply the found handler
	else:
		# then we read the handler config
		h.read_conf(Conf)

		if mesg.is_multipart():
			# Give each part of message to handler
			for part in mesg.walk():
				# Consider all responses we may have
				for response in h.handle(part):
					attach(resp, response)
				
		else:
			# Call handle just once with message payload
			for response in h.handle(mesg):
				attach(resp, response)

	# Then we send the mail
	log.notice("Sending from %s to  %s \n" % (MBOT_ADDRESS, sender))
	s = smtplib.SMTP()
	s.connect()
	s.sendmail(MBOT_ADDRESS, sender, resp.as_string())
	s.close()

if __name__ == "__main__":
	main()
