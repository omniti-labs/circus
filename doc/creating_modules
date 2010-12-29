Creating New Modules
====================

Module Structure
----------------

Every command in the circonus client is in its own file, and contains a single
python class called 'Module'. This class can contain almost anything, but must
contain a 'command' method that takes one or more parameters. The first
parameter (after self) contains any options that are passed to the command,
and any other parameters that the method takes are filled in with parameters
on the command line.

For example:

    def command(self, opts, foo, bar):
        print foo, bar

This will take two command line parameters (and the names of the parameters
will show up in the help for the command), printing them out.

Each module file has several variables that can be added to the top of the
file to set various options:

__cmdname__  - The name of the command (defaults to the name of the module)
__cmdopts__  - Which options a command can accept. This is in the form that is
               sent to getopts. E.g. "axv:".
__longopts__ - A list of long options a command can take.

Using the API
-------------

The contructor to the Module object takes two arguments: api and account.
Api is a Circonus API object and can be used to make any api calls:

For example:

    rv = api.list_checks(active='true') # Returns all active checks

The return value from these checks is a data structure that is decoded from
whatever json is returned by circonus. It's usually a dictionary or list, and
the API docs should be able to tell you which (In JSON, a dictonary/hashmap is
referred to as an object).

Some notes on the api calls:

    - All calls are methods on the api object as shown in the example above.
    - All arguments must be passed as keyword arguments:
        api.list_checks('true')         # <-- this does NOT work
        api.list_checks(active='true')  # <-- Do this instead
    - See lib/circonusapi.py for which api calls are available and what
      parameters they can take. All of the information is stored in the
      self.methods variable near the top of the file.

API Exceptions
--------------

Any errors in an api call will throw a circonusapi.CirconusAPIError exception.
This exception has a couple of attributes you can use: e.code (HTTP return
code), e.success (whether the call succeeded - it probably didn't if you're
reading this as part of the error), and e.error (the error message returned by
the API).

A good pattern for the api calls is something like this:

    import circonusapi

    print "Adding graph"
    try:
        checks = api.add_graph(graph_data=graph_data)
        print "Success"
    except circonusapi.CirconusAPIError, e:
        print "Failed - %s" % e.error
