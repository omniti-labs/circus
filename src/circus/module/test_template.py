__cmdname__ = "test_template"

import json
import os
import sys

import util

class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, template_type, template_name, *params):
        """Prints out a template with parameters substituted

        Arguments:
            template_type   -- the type of the template
            template_name   -- the name of the template file
            params          -- parameters (see below)

        Other parameters are specified as "param_name=value" and will
        be substituted in the template. Use {param_name} in the template.

        If a 'target' parameter is given, then a 'targetip' parameter will
        be automatically provided and will resolve to the IP address pointed
        to by the target hostname (if it is a hostname).
        """
        template_dir = os.path.join(os.path.dirname(__file__),
                                  "..", "templates", template_type)
        template = util.Template(template_name, template_dir)
        params = template.parse_nv_params(params)
        if 'target' in params:
            params['targetip'] = util.resolve_target(params['target'])

        substituted = template.sub(params)
        print json.dumps(substituted, indent=4)
