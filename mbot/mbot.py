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
import ConfigParser, time, socket

# All this will be used to create the response mail
from email import Encoders
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

CONFIG_FILE  = "./mbot.conf"
MBOT_ADDRESS = "mbot@localhost"
LOG_LEVEL    = "debug"
SECTIONS     = ""

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

def usage():
	""" print out the command usage """
	command = os.path.basename(sys.argv[0])
	print "%s [-c <config_file>]" % command

def main():
	""" Here we do the job """
	global MBOT_ADDRESS, CONFIG_FILE, LOG_LEVEL

	config_file = CONFIG_FILE
	try:
		opts, args = getopt.getopt(sys.argv[1:], "c:")
	except getopt.GetoptError:
		# print help information and exit:
		usage()
		sys.exit(2)

	for o, a in opts:
		if o == "-c":
			config_file = a

	Conf = read_defaults(config_file)
	log  = Logger.Logger(LOG_LEVEL)
	
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
	date    = mesg.get('Date')
	dest    = mesg.get('To')
	
	log.notice("Incoming mail: the %s, from '%s' [%s] to '%s' " \
		   % (date, sender, mesg_id, dest) + \
		   "with subject '%s'" % subject)

	# we only consider (parse) the text/plain parts of message
	if mesg.is_multipart():
		body = []
		for part in mesg.walk():
			if part.get_content_type() == "text/plain":
				body.append(part.get_payload(decode=1))
			else:
				body.append(part)
	else:
		body = [mesg.get_payload()]

	log.notice("message: %s %s %s \n" % (mesg_id, sender, subject))

	# we prepare the response
	resp = MIMEMultipart()
	resp['Subject']     =  'Re: %s' % subject
	resp['To']          = sender
	resp['In-Reply-To'] =  mesg_id

	# we initialize a handler corresponding to the given subject
	# first we create a new dict reverse from module one
	rev_modules = {}
	for section in SECTIONS:
		log.debug("section: %s" % section)
		subjects = section.split(',')
		handler  = Conf.get(section, 'handler')
		log.debug("subjects: %s for handler: %s" % (subjects, handler)
		for subject in subjects:
			rev_modules[subject] = handler
			log.debug("subject: %s" % subject)
	log.debug("Modules by subject: %s" % rev_modules)

	# now we can try to import appropriate module and use it
	h = None
	for s in rev_modules:
		if subject.find(s) == 0:
			handler = rev_modules[s]
			log.debug("using handler: %s" % handler)
			try:
				handlerModule = __import__(handler)
				log.notice("Using handler: %s" % handler)
				handlerClass = getattr(handlerModule, handler)
				log.debug("handlerClass: %s" % handlerClass)
				h = handlerClass(log, subject[len(s):],
						 dest, sender, date)
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

	# Here we apply the found handler
	else:
		# then we read the handler config
		h.read_conf(Conf)

		# we pass each part of the message to the handler
		for part in body:
			for (type, out) in h.handle(part):
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

				resp.attach(data)

	# Then we send the mail
	log.notice("Sending from %s to  %s \n" % (MBOT_ADDRESS, sender))
	s = smtplib.SMTP()
	s.connect()
	s.sendmail(MBOT_ADDRESS, sender, resp.as_string())
	s.close()

if __name__ == "__main__":
	main()
