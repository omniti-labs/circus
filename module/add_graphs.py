__cmdname__ = "add_graphs"
__cmdopts__ = "cg"

import json
import logging
import re
import sys
import urllib2

import graphutil
import util

import circonusapi

class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, template_name, pattern):
        """Add graphs in bulk based on a template

        template_name   - the name of the template file
        pattern         - a regex to match on check names

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
            template = graphutil.Template(template_name)
        except IOError:
            print "Unable to open template %s" % template_name
            sys.exit(1)
        checks, groups = self.find_checks(pattern)
        self.verify_metrics(template, checks)
        print "About to add %s graphs for the following checks:" % (
            template_name)
        for c in checks:
            print "    %s (%s)" % (c['name'], c['agent'])
        if not util.confirm():
            print "Not adding graphs."
            sys.exit()
        self.add_graphs(template, checks, groups)

    def find_checks(self, pattern):
        print "Retrieving matching checks"
        all_checks = self.api.list_checks()
        filtered_checks = []
        groups = {}
        for c in sorted(all_checks):
            m = re.search(pattern, c['name'])
            if m:
                filtered_checks.append(c)
                # Store numbered groups
                matchgroups = m.groups()
                groups[c['check_id']] = {}
                for i in range(0, len(matchgroups)):
                    groups[c['check_id']]["group%s" % (i+1)] = matchgroups[i]
                # Store named groups - (?P<name>...)
                groups[c['check_id']].update(m.groupdict())
        return filtered_checks, groups

    def verify_metrics(self, template, checks):
        print "Verifying that checks have the correct metrics"
        template_metrics = template.get_metrics()
        checks_with_wrong_metrics = []
        for c in checks:
            metrics = self.api.list_metrics(check_id=c['check_id'])
            metric_name_types = [
                {'name': m['name'], 'type': m['type']} for m in metrics]
            for m in template_metrics:
                if m not in metric_name_types:
                    checks_with_wrong_metrics.append({
                        'name': c['name'],
                        'metric': m['name'],
                        'type': m['type']})
        if checks_with_wrong_metrics:
            print "The following checks do not have metrics specified in" \
                    " the template:"
            for c in checks_with_wrong_metrics:
                print "    %(name)s - %(metric)s (%(type)s)" % c
            print "Not adding graphs. The template does not match the checks"
            sys.exit(1)

    def add_graphs(self, template, checks, groups):
        for c in checks:
            params = {
                "check_name":   c['name'],
                "check_id":     c['check_id'],
                "check_target": c['target'],
                "check_agent":  c['agent']
            }
            params.update(groups[c['check_id']])
            graph_data = template.sub(params)
            print "Adding graph: %s..." % graph_data['title'],
            try:
                rv = self.api.add_graph(graph_data = json.dumps(graph_data))
                print "Success"
            except circonusapi.CirconusAPIError, e:
                print "Failed\n    %s" % e.error
