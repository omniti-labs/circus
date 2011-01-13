import ConfigParser
import getopt
import os
import sys

# Add the lib dir to the current python path - allows modules to use utility
# libraries
sys.path.append(os.path.dirname(__file__))

import circonusapi
import cmdparse
import log

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


        self.options = self.cmdparser.parse_options()
        self.init_logger(self.options['debug'])
        self.config = self.load_config(self.options['conffile'])
        self.debug = self.config.getboolean('general', 'debug')
        self.api = circonusapi.CirconusAPI(self.get_api_token())
        self.account = self.get_current_account()
        self.load_modules()

    def load_modules(self):
        tmp = [os.path.splitext(i) for i in os.listdir(
            os.path.join(os.path.dirname(__file__), "module")) ]
        module_list = [i[0] for i in tmp
                       if i[1] == '.py' and i[0] != '__init__']

        modules = []
        for modname in module_list:
            try:
                module = __import__('module.%s' % modname, globals(),
                                    locals(), [modname])
            except ImportError, e:
                log.error("Unable to load module %s: %s" % (modname, e))
                continue
            module_object = module.Module(self.api, self.account)
            modules.append(module_object)
            # Register commands
            # use __cmdname__ for the command name, falling back to the name
            # of the module if it's not present
            cmdname = getattr(module, '__cmdname__', modname)
            cmdopts = getattr(module, '__cmdopts__', '')
            longopts = getattr(module, '__longopts__', [])
            self.cmdparser.add(cmdname, module_object.command,
                               opts=cmdopts, longopts=longopts)
        return modules

    def init_logger(self, debug):
        if debug:
            log.debug_enabled = True
        log.debug("Debugging mode on")

    def load_config(self, configfile):
        config = ConfigParser.SafeConfigParser()

        # First load the default config
        try:
            config.readfp(open(os.path.join(os.path.dirname(__file__),
                                                 "data", "defaults")))
            log.debug("Loaded default configuration")
        except IOError:
            log.error("Unable to load default configuraiton. The program"
                    " may not work correctly.")

        # Now load the system/user specific config (if any)
        if configfile:
            loaded = config.read([configfile])
        else:
            loaded = config.read(['/etc/circusrc',
                                  os.path.expanduser('~/.circusrc')])
        log.debug("Loaded config files: %s" % ', '.join(loaded))
        return config

    def get_api_token(self):
        account = self.get_current_account()
        try:
            token = self.config.get('tokens', account)
        except ConfigParser.NoOptionError:
            log.error("No token found for account %s. Please set one"
                            " up in the config file" % account)
            sys.exit(1)
        return token

    def get_current_account(self):
        account = self.options['account']
        if not account:
            account = self.config.get('general', 'default_account')
            if not account:
                log.error("No default account has been set up"
                              " and one wasn't specified on the command line")
                sys.exit(1)
        return account

    def start(self):
        try:
            status = self.cmdparser.parse()
        except circonusapi.AccessDenied:
            log.error(
                "Access denied. Perhaps you need to generate a new token")
            status = 1
        except circonusapi.TokenNotValidated:
            log.error("API token requires validation")
            status = 1

        if status:
            sys.exit(status)

if __name__ == '__main__':
    cc = CirconusClient()
    cc.start()
