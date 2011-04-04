# cmdparser.py
#
# Copyright 2011 Mark Harrison. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import getopt
import inspect
import shlex
import sys
try:
    import readline
except ImportError:
    readline = None

class Parser(object):
    def __init__(self, scriptname=sys.argv[0], interactive=False):
        self.cmd_map = {}
        self.scriptname = scriptname
        self.interactive = interactive
        self.add('help', self.help)
        self.options = {}
        self.args = None

    def add(self, cmd, callback, description="", opts="", longopts=[]):
        """Add a command to the list of accepted commands.

        cmd         - the name of the command
        callback    - function to call if the command is encountered.
                      the parameters to the callback are a single variable
                      containing a list of options passed to the command, and
                      then the rest of the non-option arguments.
        description - what the command does, printed in the usage summary
                      if description isn't provided, use the first line of the
                      callback's docstring if present.
        opts        - A string of short option letters that  the command takes.
                      This is the same format as that accepted by the built-in
                      getopt module.
        longopts    - A list of strings containing long options that the
                      command takes. This also is the same as that accepted by
                      the built-in getopt module.
        """
        if not description and callback.__doc__:
            description = callback.__doc__.splitlines()[0]
        self.cmd_map[cmd] = {
            'callback': callback,
            'description': description,
            'opts': opts,
            'longopts': longopts}

    def addopt(self, shortopt, var, longopt=None, doc="", takesparam=False,
               default=None):
        """Add an option to the list of valid global options.

        shortopt    - the short name for the option (single letter)
        var         - the name of the variable to store the option value in.
                      This will be a dictionary entry.
        longopt     - an optional long version of the option (word)
        doc         - A single line help string for the option
        takesparam  - Does the option require a parameter? If not, it will be a
                      boolean value.
        default     - The default value for the option if not specified.
        """

        if default is None and not takesparam:
            default = False

        self.options[var] = {
            'short': shortopt,
            'long': longopt,
            'doc': doc,
            'takesparam': takesparam,
            'default': default}

    def _cmd_usage(self, cmd):
        """Prints the usage information for a command.

        It looks at the callback function for the command and works out what
        arguments the commmand takes based on that and prints out a simple
        usage summary showing required/optional argument names.
        """
        callback = self.cmd_map[cmd]['callback']
        argspec = inspect.getargspec(callback)
        args = argspec[0]
        # Get mandatory/optional args
        if argspec[3]:
            optargs = args[-len(argspec[3]):]
            args = args[:-len(argspec[3])]
        else:
            optargs = []
        # Show *args parameters if present
        if argspec[1]:
            optargs.append("%s..." % argspec[1])
        if args[0] == 'self':
            args = args[1:]
        args = args[1:]     # Strip off the mandatory opts argument
        optstr = ""
        if self.cmd_map[cmd]['opts'] or self.cmd_map[cmd]['longopts']:
            optstr = " [OPTIONS]..."
        print "usage: %s %s%s %s %s" % (self.scriptname, cmd, optstr,
            ' '.join(['%s' % arg.upper() for arg in args]),
            ' '.join(['[%s]' % arg.upper() for arg in optargs]))

    def help(self, opts, command=None):
        """Print help information for a command"""
        if not command:
            self.usage()
            return
        try:
            docs = self.cmd_map[command]['callback'].__doc__
        except KeyError:
            print "No such command:", command
            return
        self._cmd_usage(command)
        print
        # Print usage
        if docs:
            print self._trim_docstring(docs)
        elif self.cmd_map[command]['description']:
            print self.cmd_map[command]['description']
        else:
            print "No help available for", command

    def _interactive_console(self):
        self.scriptname = "" # For usage messages
        if readline:
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self._tab_completer)
        while True:
            try:
                line = raw_input("> ")
            except (EOFError, KeyboardInterrupt):
                print
                return
            args = shlex.split(line)
            self.parse(args)

    def parse(self, args=None, _currently_interactive=False):
        if not args:
            args = self.args
        if not args:
            args = sys.argv[1:]

        if not args and self.interactive and not _currently_interactive:
            self._interactive_console()
            sys.exit(0)

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
        # Funcargs[1] means that we have a *args parameter and so we can have
        # as many args as we want
        if arglen >= minlen and (funcargs[1] or arglen <= maxlen):
            return callback(cmdopts, *args[1:])
        else:
            self._cmd_usage(cmd)
            print "    %s" % self.cmd_map[cmd]['description']
            return 1

    def parse_options(self, exit_on_error=True):
        """Parse any global options that are provided.

        Returns a dictionary whose keys are the option name and the value is
        the value of any argument given, or simply True if the option does not
        take an argument.

        exit_on_error - if true, will run sys.exit(1) on error. If false, it
                        will return None. Note that you will need to check
                        explicitly for None as an empty dict will be returned
                        if no options are given on the command line and this
                        also evaluates to False in a boolean check.
        """
        options = {}
        shortopts = []  # List of short options (passed to getopt)
        longopts = []   # List of long options (passed to getopt)
        optmap = {}     # Mapping of option strings to varnames
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
            if exit_on_error:
                sys.exit(1)
            return None

        for o, a in opts:
            try:
                var = optmap[o]
            except KeyError:
                print "Unhandled option: %s" % o
                if exit_on_error:
                    sys.exit(1)
                return None
            if self.options[var]['takesparam']:
                options[var] = a
            else:
                options[var] = True

        self.args = args

        return options

    def _tab_completer(self, text, state):
        idx = readline.get_begidx()
        if idx > 0:
            # For now, don't do completion of options
            return None
        options = [i for i in self.cmd_map if i.startswith(text)]
        try:
            return options[state]
        except IndexError:
            return None

    def _trim_docstring(self, docstring):
        """Strip leading whitespace from a docstring.

        Copied from PEP-257. PEP-257 is public domain."""
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

    def usage(self):
        """Usage summary

        Shows a list of valid commands and options.
        """
        if self.scriptname:     # Scriptname is blank for interactive use
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
                        optstr = "%s, --%s" % (
                                optstr, self.options[opt]['long'])
                    print "    %-15s  %s" % (optstr, self.options[opt]['doc'])
        print "commands:"
        for cmd in sorted(self.cmd_map.keys()):
            print "    %-15s  %s" % (cmd, self.cmd_map[cmd]['description'])
