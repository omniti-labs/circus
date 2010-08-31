import inspect
import sys
import getopt

class CmdParse(object):
    def __init__(self, options=None):
        self.cmd_map = {}
        self.scriptname = sys.argv[0]
        self.add('help', self.help)
        self.options = {}
        self.args = None

    def parse_options(self):
        options = {}
        shortopts = [] # List of short options (passed to getopt)
        longopts = [] # List of long options (passed to getopt)
        optmap = {} # Mapping of option strings to varnames
        for opt in self.options:
            vals = self.options[opt]
            options[opt] = vals['default']

            shortopts.append(vals['short'])
            if vals['takesparam']:
                shortopts.append(":")
            optmap["-%s" % vals['short']] = opt

            if vals['long']:
                optstr = vals['long']
                if vals['takesparam']:
                    optstr = "%s=" % optstr
                longopts.append(optstr)
                optmap["--%s" % vals['long']] = opt

        try:
            opts, args = getopt.getopt(sys.argv[1:], ''.join(shortopts),
                    longopts)
        except getopt.GetoptError, e:
            print str(e)
            self.usage()
            sys.exit(1)

        for o, a in opts:
            try:
                var = optmap[o]
            except KeyError:
                print "Unhandled option: %s" % o
                sys.exit(1)
            if self.options[var]['takesparam']:
                options[var] = a
            else:
                options[var] = True

        self.args = args

        return options

    def parse(self, args=None):
        if not args:
            args = self.args
        if not args:
            args = sys.argv[1:]

        try:
            cmd = args[0]
            callback = self.cmd_map[cmd]['callback']
        except (IndexError, KeyError):
            self.usage()
            return 1
        # Parse options after the command itself
        if self.cmd_map[cmd]['opts'] or self.cmd_map[cmd]['longopts']:
            try:
                cmdopts, args = getopt.gnu_getopt(
                    args, self.cmd_map[cmd]['opts'],
                    self.cmd_map[cmd]['longopts'])
            except getopt.GetoptError, e:
                print "Error:", e
                args = []
        else:
            cmdopts = ()

        # Check that the number of args on the command line matches that of
        # the callback function (self doesn't count as an argument, and we
        # require that the first argument be the options)
        arglen = len(args) + 1
        funcargs = inspect.getargspec(callback)
        if funcargs[0][0] != 'self':
            arglen -= 1
        # Need to have at least as many mandatory and no more than
        # mandatory+optional arguments
        maxlen = len(funcargs[0])
        if funcargs[3]:
            minlen = maxlen - len(funcargs[3])
        else:
            minlen = maxlen
        if arglen >= minlen and arglen <= maxlen:
            return callback(cmdopts, *args[1:])
        else:
            self.cmd_usage(cmd)
            print "    %s" % self.cmd_map[cmd]['description']
            return 1

    def usage(self):
        if self.options:
            print "usage: %s [options] [command] [args]" % self.scriptname
        else:
            print "usage: %s [command] [args]" % self.scriptname
        print
        if self.options:
            print "options:"
            for opt in sorted(self.options):
                optstr = "-%s" % self.options[opt]['short']
                if self.options[opt]['long']:
                    optstr = "%s, --%s" % (optstr, self.options[opt]['long'])
                print "    %-15s  %s" % (optstr, self.options[opt]['doc'])
        print "commands:"
        for cmd in sorted(self.cmd_map.keys()):
            print "    %-15s  %s" % (cmd, self.cmd_map[cmd]['description'])

    def cmd_usage(self, cmd):
        callback = self.cmd_map[cmd]['callback']
        argspec = inspect.getargspec(callback)
        args = argspec[0]
        # Get mandatory/optional args
        if argspec[3]:
            optargs = args[-len(argspec[3]):]
            args = args[:-len(argspec[3])]
        else:
            optargs = []
        if args[0] == 'self':
            args = args[1:]
        args = args[1:] # Strip off the mandatory opts argument
        optstr = ""
        if self.cmd_map[cmd]['opts'] or self.cmd_map[cmd]['longopts']:
            optstr = " [OPTIONS]..."
        print "usage: %s %s%s %s %s" % (self.scriptname, cmd, optstr,
            ' '.join([ '%s' % arg.upper() for arg in args ]),
            ' '.join([ '[%s]' % arg.upper() for arg in optargs]))

    def add(self, cmd, callback, description="", opts="", longopts=[]):
        """Add a command to the list of commands.

        cmd      -  the name of the command
        callback -  function to call if the command is encountered.
                    the rest of the arguments are passed to the callback
        description - what the command does, printed in the usage summary
                    if description isn't provided, use the first line of the
                    callback's docstring if present.
        """
        if not description and callback.__doc__:
            description = callback.__doc__.splitlines()[0]
        self.cmd_map[cmd] = {
            'callback': callback,
            'description': description,
            'opts': opts,
            'longopts': longopts
        }

    def addopt(self, shortopt, var, longopt=None, doc="", takesparam=False,
               default=None):
        """Add an option to the list of valid options.

        shortopt - the short name for the option (single letter)
        var - the name of the variable to store the option value in. This
              will be a dictionary entry.
        longopt - an optional long version of the option (word)
        doc - A single line help string for the option
        takesparam - Does the option require a parameter? If not, it will be a
                     boolean value.
        default - The default value for the option if not specified.
        """

        if default is None and not takesparam:
            default = False

        self.options[var] = {
            'short': shortopt,
            'long': longopt,
            'doc': doc,
            'takesparam': takesparam,
            'default': default
        }

    def help(self, opts, command=None):
        """Provides help for a command"""
        if not command:
            self.usage()
            return
        try:
            docs = self.cmd_map[command]['callback'].__doc__
        except KeyError:
            print "No such command:", command
            return
        self.cmd_usage(command)
        print
        # Print usage
        if docs:
            print self.trim_docstring(docs)
        elif self.cmd_map[command]['description']:
            print self.cmd_map[command]['description']
        else:
            print "No help available for", command

    def trim_docstring(self, docstring):
        """Copied from PEP-257"""
        if not docstring:
            return ''
        # Convert tabs to spaces (following the normal Python rules)
        # and split into a list of lines:
        lines = docstring.expandtabs().splitlines()
        # Determine minimum indentation (first line doesn't count):
        indent = sys.maxint
        for line in lines[1:]:
            stripped = line.lstrip()
            if stripped:
                indent = min(indent, len(line) - len(stripped))
        # Remove indentation (first line is special):
        trimmed = [lines[0].strip()]
        if indent < sys.maxint:
            for line in lines[1:]:
                trimmed.append(line[indent:].rstrip())
        # Strip off trailing and leading blank lines:
        while trimmed and not trimmed[-1]:
            trimmed.pop()
        while trimmed and not trimmed[0]:
            trimmed.pop(0)
        # Return a single string:
        return '\n'.join(trimmed)
