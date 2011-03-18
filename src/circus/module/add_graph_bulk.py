__cmdname__ = "add_graph_bulk"

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

    def command(self, opts, template_name, pattern):
        """Add graphs for multiple checks in bulk based on a template

        Arguments:
            template_name   -- the name of the template file
            pattern         -- a regex to match on check names

        The templates are in json, and is in the same format as the output of
        the dump_graph command.

        Various string subsitutions can be used:

        {check_id}     - The check ID
        {check_name}   - The check name
        {check_target} - The target of the check (IP address)
        {check_agent}  - The agent the check is run from
        {groupN}       - Matching groups (the parts in parentheses) in the
                         pattern given on the command line. (replace N with
                         a group number)

        You can also use named matching groups - (?P<groupname>...) in the
        pattern and {groupname} in the graph template.
        """
        try:
            template = util.GraphTemplate(template_name)
        except IOError:
            log.error("Unable to open template %s" % template_name)
            sys.exit(1)
        checks, groups = util.find_checks(self.api, pattern)
        util.verify_metrics(self.api, template, checks)
        log.msg("About to add %s graphs for the following checks:" % (
            template_name))
        for c in checks:
            log.msg("    %s (%s)" % (c['name'], c['agent']))
        if not util.confirm():
            log.msg("Not adding graphs.")
            sys.exit()
        self.add_graphs(template, checks, groups)

    def add_graphs(self, template, checks, groups):
        for c in checks:
            params = {
                "check_name":   c['name'],
                "check_id":     c['check_id'],
                "check_target": c['target'],
                "check_agent":  c['agent']}
            params.update(groups[c['check_id']])
            graph_data = template.sub(params)
            log.msgnb("Adding graph: %s..." % graph_data['title'])
            try:
                rv = self.api.add_graph(graph_data=json.dumps(graph_data))
                log.msgnf("Success")
            except circonusapi.CirconusAPIError, e:
                log.msgnf("Failed")
                log.error(e.error)
