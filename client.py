#!/usr/bin/env python

import ConfigParser
import getopt
import logging
import os
import sys

import circonusapi
import cmdparse

class CirconusClient(object):
    def __init__(self):
        self.cmdparser = cmdparse.CmdParse()
        self.cmdparser.addopt(shortopt="d", longopt="debug",
                              var="debug", doc="Enable Debug Mode",
                              takesparam=False, default=False)
        self.cmdparser.addopt(shortopt="c", longopt="conf", var="conffile",
                              doc="Specify an alternate configuration file",
                              takesparam=True, default=None)
        # Add commands here
        self.cmdparser.add("list_accounts", self.list_accounts)

        self.options = self.cmdparser.parse_options()
        self.init_logger(self.options['debug'])
        self.config = self.load_config(self.options['conffile'])
        self.debug = self.config.getboolean('general', 'debug')
        self.api = circonusapi.CirconusAPI(self.config.get('general', 'token'))

    def init_logger(self, debug):
        if debug:
            level = logging.DEBUG
        else:
            level=logging.INFO
        logging.basicConfig(level=level,
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        logging.info("progname starting...")
        logging.debug("Debugging mode on")

    def load_config(self, configfile):
        config = ConfigParser.SafeConfigParser()

        # First load the default config
        try:
            config.readfp(open(os.path.join(os.path.dirname(__file__),
                                                 "data", "defaults")))
            logging.debug("Loaded default configuration")
        except IOError:
            logging.error("Unable to load default configuraiton. The program"
                    " may not work correctly.")

        # Now load the system/user specific config (if any)
        if configfile:
            loaded = config.read([configfile])
        else:
            loaded = config.read(['/etc/circusrc', '~/.circusrc'])
        logging.debug("Loaded config files: %s" % ', '.join(loaded))
        return config

    def start(self):
        status = self.cmdparser.parse()
        if status:
            sys.exit(status)

    def list_accounts(self, opts):
        """List the accounts you have access to"""
        rv = self.api.list_accounts()
        for account in sorted(rv):
            print account

if __name__ == '__main__':
    cc = CirconusClient()
    cc.start()

