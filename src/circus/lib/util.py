"""Various utility functions"""
import log
import sys
import os
import re
import json
import socket


def confirm(text="OK to continue?"):
    response = None
    while response not in ['Y', 'y', 'N', 'n']:
        response = raw_input("%s (y/n) " % text)
    if response in ['Y', 'y']:
        return True
    return False


def get_agent(api, agent_name):
    rv = api.list_agents()
    agents = dict([(i['name'], i['agent_id']) for i in rv])
    try:
        return agents[agent_name]
    except KeyError:
        log.error("Invalid/Unknown Agent: %s" % agent_name)
        log.msg("Valid Agents:")
        for a in agents:
            log.msgnf("    %s" % a)
        sys.exit(1)


def resolve_target(target):
    """Resolves a target name into an IP. Allows specifying targets by name
    on the command line."""
    return socket.gethostbyname(target)


class Template(object):
    """Generic template class for json templates"""
    def __init__(self, name, template_dir):
        try:
            # Try the current directory first
            fh = open(name)
        except IOError:
            # Then try the template directory
            fh = open(os.path.join(template_dir, "%s.json" % name))
        self.template = json.load(fh)
        fh.close()

    def sub(self, params):
        """Substitute parameters in the template"""
        return self._process(self.template, params)

    def parse_nv_params(self, params):
        """Parses a list of params in the form name=value into a dict
        suitable for passing to Template.sub"""
        template_params = {}
        for param in params:
            try:
                name, value = param.split('=', 1)
            except ValueError:
                log.error("Invalid parameter: %s" % param)
                log.error("Extra parameters must be specified as name=value")
                sys.exit(1)
            template_params[name] = value
        return template_params

    def _process(self, i, params):
        if type(i) == dict:
            return self._process_dict(i, params)
        if type(i) == list:
            return self._process_list(i, params)
        if type(i) == str or type(i) == unicode:
            return self._process_str(i, params)
        return i

    def _process_dict(self, d, params):
        new_d = {}
        for k, v in d.items():
            new_k = self._process_str(k, params)
            new_d[new_k] = self._process(v, params)
        return new_d

    def _process_list(self, l, params):
        new_l = []
        for i in l:
            new_l.append(self._process(i, params))
        return new_l

    def _process_str(self, s, params):
        return re.sub("{(\S+)}", lambda m: params[m.group(1)], s)


class GraphTemplate(Template):
    def __init__(self, name):
        template_dir = os.path.join(
            os.path.dirname(__file__), "..", "templates", "graph")
        super(GraphTemplate, self).__init__(name, template_dir)

    def get_metrics(self):
        """Returns a list of metrics specified in the graph template"""
        return [i['metric_name'] for i in self.template['datapoints']]

    def _process_str(self, s, params):
        # Special case the check_id - make it an integer if it's the only
        # thing present in the string
        if s == "{check_id}":
            return int(params['check_id'])
        return super(GraphTemplate, self)._process_str(s, params)


class RuleTemplate(Template):
    def __init__(self, name):
        template_dir = os.path.join(
            os.path.dirname(__file__), "..", "templates", "rule")
        super(RuleTemplate, self).__init__(name, template_dir)

    def get_metrics(self):
        """Returns a list of metrics specified in the graph template"""
        return [i['metric_name'] for i in self.template]

    def _process_str(self, s, params):
        # Special case the check_id - make it an integer if it's the only
        # thing present in the string
        if s == "{check_id}":
            return int(params['check_id'])
        return super(RuleTemplate, self)._process_str(s, params)


def find_checks(api, pattern):
    log.msg("Retrieving matching checks")
    all_checks = api.list_checks(active='true')
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
                groups[c['check_id']]["group%s" % (i + 1)] = matchgroups[i]
            # Store named groups - (?P<name>...)
            groups[c['check_id']].update(m.groupdict())
    return filtered_checks, groups


def verify_metrics(api, template, checks):
    log.msg("Verifying that checks have the correct metrics")
    template_metrics = template.get_metrics()
    checks_with_wrong_metrics = []
    count = 0
    for c in checks:
        count += 1
        print "\r%s/%s" % (count, len(checks)),
        sys.stdout.flush()
        metrics = api.list_metrics(check_id=c['check_id'])
        metric_names = [m['name'] for m in metrics]
        for m in template_metrics:
            if m not in metric_names:
                checks_with_wrong_metrics.append({
                    'name': c['name'],
                    'metric': m['name']})
    if checks_with_wrong_metrics:
        log.msg("The following checks do not have metrics specified in"
                " the template:")
        for c in checks_with_wrong_metrics:
            log.msg("%(name)s - %(metric)s" % c)
        log.error("Not continuing. The template does not match the"
                    " checks")
        sys.exit(1)
    print
