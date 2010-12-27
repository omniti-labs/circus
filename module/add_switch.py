__cmdname__ = "add_switch"
__cmdopts__ = "cg"

import logging
import sys

import graphutil

class Module(object):
    def __init__(self, api, account):
        # OID prefixes
        prefix_1 = ".1.3.6.1.2.1.2.2.1"
        prefix_2 = ".1.3.6.1.2.1.31.1.1.1"

        self.metrics = {
            'status':       "%s.8"  % prefix_1,
            'name':         "%s.18" % prefix_2,
            'speed':        "%s.5"  % prefix_1,
            'in_octets':    "%s.6"  % prefix_2, # 64-bit version
            'out_octets':   "%s.10" % prefix_2, # 64-bit counter
            'in_errors':    "%s.14" % prefix_1,
            'out_errors':   "%s.20" % prefix_1
        }
        self.api = api
        self.account = account

    def command(self, opts, target, agent, community, port_count,
                friendly_name):
        rv = self.api.list_agents()
        agents = dict([(i['name'], i['agent_id']) for i in rv])
        try:
            self.agent = agents[agent]
        except KeyError:
            logging.error("Invalid/Unknown Agent: %s" % agent)
            sys.exit(1)
        self.target = target
        self.community = community
        self.port_count = port_count
        self.friendly_name = friendly_name
        if ('-c', '') in opts or not opts:
            self.add_check()
        if ('-g', '') in opts or not opts:
            self.add_graphs()

    def add_check(self):
        for i in range(1, int(self.port_count)):
            logging.debug("Adding port %s" % i)
            metric_names = []
            params = {
                    'account': self.account,
                    'agent_id' : self.agent,
                    'target' : self.target,
                    'module' : "snmp",
                    'display_name_%s' % self.target :
                        "%s port %s interface stats" % (self.friendly_name, i),
                    'community' : self.community,
            }
            for k in self.metrics:
                metric_names.append(k)
                params["oid_%s" % k] = "%s.%s" % (self.metrics[k], i)
            params['metric_name'] = metric_names

            for k in sorted(params):
                logging.debug("%20s = %s" % (k, params[k]))

            logging.debug("Adding check bundle")
            #rv = self.api.add_check_bundle(**params)
            # TODO - get check ID and store it for adding graphs

    def add_graphs(self):
        # TODO - move this into a separate command for adding graphs
        # plan (from task post):
        # search for checks with a certain name (regex filter?), create the
        # graph with that check ID and the relevant metrics (we can use
        # json/python dicts for the graph template itself and pass it almost
        # directly). We just need to make sure that the relevant metrics are
        # available.
        t = graphutil.Template("switch")
        check_ids = {1: 1234, 2:1235} # TODO - Get real check IDs
        params = {
            "switch_name": self.friendly_name,
        }
        for c in check_ids:
            params['check_id'] = check_ids[c]
            params['port'] = c
            print t.sub(params)
