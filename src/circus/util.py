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
        with open(os.path.join(template_dir, "%s.json" % name)) as fh:
            self.template = json.load(fh)

    def sub(self, params):
        """Substitute parameters in the template"""
        return self._process(self.template, params)

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
