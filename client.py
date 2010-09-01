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
        self.cmdparser.add("list_accounts", self.list_accounts, opts="l")

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
            loaded = config.read(['/etc/circusrc',
                                  os.path.expanduser('~/.circusrc')])
        logging.debug("Loaded config files: %s" % ', '.join(loaded))
        return config

    def start(self):
        status = self.cmdparser.parse()
        if status:
            sys.exit(status)

    def list_accounts(self, opts):
        """List the accounts you have access to

        Options:
            -l - Long listing (show metric count)
        """
        rv = self.api.list_accounts()
        print "Account List"
        for account in sorted(rv):
            desc = ""
            if account['account_description']:
                desc = " (%s)" % account['account_description']
            print "    %s%s" % (account['account_name'], desc)
            if ('-l', '') in opts:
                print "        Circonus metrics:   %s/%s" % (
                    account['circonus_metrics_used'],
                    account['circonus_metric_limit'])
                if 'enterprise_metric_limit' in account:
                    print "        Enterprise metrics: %s/%s" % (
                        account['enterprise_metrics_used'],
                        account['enterprise_metric_limit'])

if __name__ == '__main__':
    cc = CirconusClient()
    cc.start()

