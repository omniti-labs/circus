__cmdname__ = "add_graph"

import json
import log
import re
import sys

import util

import circonusapi


class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, template_name, *params):
        """Add a single graph based on a template

        Arguments:
            template_name   -- the name of the template file
            params          -- other parameters (see below)

        The templates are in json, and is in the same format as the output of
        the dump_graph command.

        Other parameters are specified as "param_name=value" and will
        be substituted in the template. Use {param_name} in the template.
        """
        try:
            template = util.GraphTemplate(template_name)
        except IOError:
            log.error("Unable to open template %s" % template_name)
            sys.exit(1)
        template_params = template.parse_nv_params(params)
        graph_data = template.sub(template_params)
        log.msgnb("Adding graph: %s..." % graph_data['title'])
        try:
            rv = self.api.add_graph(graph_data=json.dumps(graph_data))
            log.msgnf("Success")
        except circonusapi.CirconusAPIError, e:
            log.msgnf("Failed")
            log.error(e.error)
