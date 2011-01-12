__cmdname__ = "add_check"

import json
import os
import sys

import util

import circonusapi

class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, template_name, check_name, target, agent, *params):
        """Adds a check based on a template

        Arguments:
            template_name   -- the name of the template file
            check_name      -- the name for the check
            target          -- the target of the check
            agent           -- the agent to run the check from
            params          -- other parameters (see below)

        Other parameters are specified as "param_name=value" and will add to
        or override anything already provided in the template. Items in the
        template that have the value of "{REQUIRED}" must be specified on the
        command line. An example of this is the url parameter for the http
        check.
        """
        template = self.check_template(template_name)
        for param in params:
            try:
                name, value = param.split('=', 1)
            except ValueError:
                print "Invalid parameter: %s" % param
                print "Extra parameters must be specified as name=value"
                sys.exit(1)
            template[name] = value

        # Add other parameters
        template['agent_id'] = util.get_agent(self.api, agent)
        template['target'] = target
        template['display_name_%s' % target] = check_name

        for k in template:
            if template[k] == '{REQUIRED}':
                print "Error: extra parameter %s is required" % k
                sys.exit(1)

        self.api.add_check_bundle(**template)


    def check_template(self, template):
        template_dir=os.path.join(os.path.dirname(__file__),
                                  "..", "templates", "check")
        with open("%s/%s.json" % (template_dir, template)) as fh:
            try:
                return json.load(fh)
            except ValueError, e:
                print "Error parsing template:", e
                sys.exit(1)
