#!/usr/bin/env python2.3

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
from email.MIMEAudio import MIMEAudio
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from mimify import mime_decode_header

import MailHandler, UrlHandler, GoogleHandler, PipeHandler, NewsHandler

# default values
global DEBUG, LOGFILE, MBOT_ADDRESS, CONFIG_FILE

DEBUG        = False
LOGFILE      = "/tmp/mbot.log"
MBOT_ADDRESS = "mbot@localhost"

CONFIG_FILE  = "./mbot.conf"

def dolog(message):
	''' Turning log formating into standard way '''

	# Get pid
	pid = int(os.getpid())
	
	#Log format:
	#[Short day] [Numeric day] [Time] [Hostname] [Service[Pid]] : [Message]
	Time = time.strftime("%b %d %H:%M:%S", time.localtime())
	Hostname = socket.gethostname()
	Service = os.path.basename(sys.argv[0])
	Pid = pid
	Message = message
	
	# Log
	logline = "%s %s %s[%d] : %s" % (Time, Hostname, Service, Pid, Message)
	
	return logline

def read_defaults(configfile = CONFIG_FILE):
	''' Reading configuration file '''

	global DEBUG, LOGFILE, MBOT_ADDRESS
	
	config = ConfigParser.ConfigParser()
	config.read(configfile)
	for option in config.defaults():
		if option == 'debug':
			DEBUG = config.get('DEFAULT',option)
		elif option == 'mbot_address':
			MBOT_ADDRESS = config.get('DEFAULT',option)
		elif option == 'logfile':
			LOGFILE = config.get('DEFAULT',option)

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
	global DEBUG, LOGFILE, MBOT_ADDRESS, CONFIG_FILE

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
	
	logfile = open(LOGFILE, 'a')
	logfile.write(dolog("Using config file %s\n" % config_file))

	DEBUG = DEBUG == 'True' or DEBUG == 'true'

	# we read the mail
	mesg = read_email()

	sender  = mesg.get('From')
	subject = mime_decode_header(mesg.get('Subject'))
	mesg_id = mesg.get('Message-Id')
	date    = mesg.get('Date')
	dest    = mesg.get('To')

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

	logfile.write(dolog("message: %s %s %s \n" %
			    (mesg_id, sender, subject)))

	# we prepare the response
	resp = MIMEMultipart()
	resp['Subject']     =  'Re: %s' % subject
	resp['To']          = sender
	resp['In-Reply-To'] =  mesg_id

	# we initialize a handler corresponding to the given subject
	if subject.find('wget') == 0:
		h = UrlHandler.UrlHandler(subject[4:])

	elif subject.find('google') == 0:
		h = GoogleHandler.GoogleHandler(subject[6:])

	elif subject.find('news') == 0:
		h = NewsHandler.NewsHandler(subject[4:], dest, sender, date)

	elif subject.find('|') == 0:
		h = PipeHandler.PipeHandler(subject[1:])

	else:
		h = MailHandler.MailHandler(subject)

	# then we read the handler config
	h.read_conf(Conf)

	for part in body:
		for (type, out) in h.handle(part):
			maintype, subtype = type.split('/', 1)
			if maintype == 'text':
				data = MIMEText(out, _subtype=subtype)
				if DEBUG:
					print out

			elif maintype == 'image':
				data = MIMEImage(out, _subtype=subtype)

			elif maintype == 'audio':
				data = MIMEAudio(out, _subtype=subtype)

			else:
				data = MIMEBase(maintype, subtype)
				data.set_payload(out)
				Encoders.encode_base64(msg)

			# When in debug mode, we do not send back mail
			if not DEBUG:
				resp.attach(data)

	# Then we send the mail
	if not DEBUG:
		logfile.write(dolog("Sending from %s to  %s \n" %
				    (MBOT_ADDRESS, sender)))
		
		s = smtplib.SMTP()
		s.connect()
		s.sendmail(MBOT_ADDRESS, sender, resp.as_string())
		s.close()

if __name__ == "__main__":
	main()
