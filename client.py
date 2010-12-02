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
        self.cmdparser.addopt(shortopt="a", longopt="account",
                              var="account",
                              doc="Specify which circonus account to use",
                              takesparam=True, default=None)
        # Add commands here
        self.cmdparser.add("list_accounts", self.list_accounts, opts="l")
        self.cmdparser.add("list_checks", self.list_checks, opts="la")

        self.options = self.cmdparser.parse_options()
        self.init_logger(self.options['debug'])
        self.config = self.load_config(self.options['conffile'])
        self.debug = self.config.getboolean('general', 'debug')
        self.api = circonusapi.CirconusAPI(self.get_api_token())

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

    def get_api_token(self):
        account = self.get_current_account()
        try:
            token = self.config.get('tokens', account)
        except ConfigParser.NoOptionError:
            logging.error("No token found for account %s. Please set one"
                            " up in the config file" % account)
            sys.exit(1)
        return token

    def get_current_account(self):
        account = self.options['account']
        if not account:
            account = self.config.get('general', 'default_account')
            if not account:
                logging.error("No default account has been set up"
                              " and one wasn't specified on the command line")
                sys.exit(1)
        return account

    def start(self):
        try:
            status = self.cmdparser.parse()
        except circonusapi.AccessDenied:
            logging.error(
                "Access denied. Perhaps you need to generate a new token")
            status = 1
        except circonusapi.TokenNotValidated:
            logging.error("API token requires validation")
            status = 1

        if status:
            sys.exit(status)

    def list_accounts(self, opts):
        """List the accounts you have access to.

        Please note that each account needs a separate API token.

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

    def list_checks(self, opts):
        """List the checks for an account

        Options:
            -l - Long listing
            -a - Include inactive and deleted checks also
        """
        active = 'true'
        if ('-a', '') in opts:
            active = ''
        rv = self.api.list_checks(active=active)
        print "Check List for %s" % self.get_current_account()
        for check in sorted(rv):
            check_active = ''
            if check['active'] == 'false':
                check_active = ' (inactive)'
            if check['active'] == 'deleted':
                check_active = ' (deleted)'
            print "    %s%s" % (check['name'], check_active)

if __name__ == '__main__':
    cc = CirconusClient()
    cc.start()

