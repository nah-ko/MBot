#!/usr/bin/env python

# mbot - a mail handling robot
#
# Author:  Dimitri Fontaine <dim@tapoueh.org>
# Author:  Christophe Truffier <toffe@nah-ko.org>
#
# This code is licensed under the GPL.
# Get yourself a version here : http://www.gnu.org/copyleft/gpl.html

# $Id$

import sys, os, syslog

class Logger:
        " Logging class for syslog or logfile use "
        # Log level dictionnary
        levels = {'debug':syslog.LOG_DEBUG,
                  'info':syslog.LOG_INFO,
                  'notice':syslog.LOG_NOTICE,
                  'warning':syslog.LOG_WARNING,
                  'err':syslog.LOG_ERR,
                  'crit':syslog.LOG_CRIT,
                  'alert':syslog.LOG_ALERT,
                  'emerg':syslog.LOG_EMERG
                 }

        def __init__(self, LogLevel="debug"):
                # Default log level
                self.log_level = self.getLevel(LogLevel)

                # Service and pid init
                Service = os.path.basename(sys.argv[0])
                Pid = int(os.getpid())

                syslog.openlog('%s[%d]' % (Service, Pid))

        def log(self, message, log_level):
                ''' Turning log formating into standard way '''
                level = self.getLevel(log_level)

                if level <= self.log_level:
                        syslog.syslog(level, message)

        def emerg(self, message):
                self.log("[EMERG] %s" % message, "emerg")

        def alert(self, message):
                self.log("[ALERT] %s" % message, "alert")

        def crit(self, message):
                self.log("[CRIT] %s" % message, "crit")

        def err(self, message):
                self.log("[ERR] %s" % message, "err")

        def warning(self, message):
                self.log("[WARNING] %s" % message, "warning")

        def notice(self, message):
                self.log("[NOTICE] %s" % message, "notice")

        def info(self, message):
                self.log("[INFO] %s" % message, "info")

        def debug(self, message):
                self.log("[DEBUG] %s" % message, "debug")

        def getLevel(self, level):
                """ Get the syslog value for log given level """
                if Logger.levels.has_key(level):
                        return Logger.levels[level]
                else:   
                        return self.default_level
