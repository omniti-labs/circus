__cmdname__ = "add_switch"
__cmdopts__ = ""

import logging
import re
import subprocess
import sys

import circonusapi
import util

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
        self.port_name_prefix = "%s.1" % prefix_2
        self.api = api
        self.account = account

    def command(self, opts, target, agent, community, friendly_name):
        """Adds snmp checks for a switch

        This command queries the switch using snmpwalk to discover what ports
        to add checks for. This requires that the snmpwalk command be
        available and that the switch be accessible over snmp from the machine
        that this command is run from.

        Arguments:
            target          -- The address of the switch
            agent           -- The name of the agent you wish circonus to use
                               for the checks
            community       -- SNMP community for the switch
            friendly_name   -- what to call the switch in the check name. This
                               is usually the (short) hostname of the switch.
        """
        # TODO - abstract this away and prompt the user for a list of
        # available agents
        rv = self.api.list_agents()
        agents = dict([(i['name'], i['agent_id']) for i in rv])
        try:
            self.agent = agents[agent]
        except KeyError:
            logging.error("Invalid/Unknown Agent: %s" % agent)
            sys.exit(1)
        self.target = util.resolve_target(target)
        self.community = community
        self.friendly_name = friendly_name
        self.ports = self.get_ports(target, community)
        print "About to add checks for the following ports:"
        for port in sorted(self.ports):
            print "   ", port
        if util.confirm():
            self.add_checks()

    def get_ports(self, target, community):
        output = subprocess.Popen(("/usr/bin/snmpwalk", "-On", "-v2c", "-c",
            community, target, self.port_name_prefix),
            stdout=subprocess.PIPE).communicate()[0]
        ports = {}
        for line in output.split("\n"):
            m = re.match(r'[.0-9]+\.(\d+) = STRING: "(?:ethernet)?([0-9/]+)"',
                        line)
            if m:
                ports[m.group(2)] = m.group(1)
        return ports

    def add_checks(self):
        for name, idx in sorted(self.ports.items()):
            print "Adding port %s..." % name,
            metric_names = []
            params = {
                    'account': self.account,
                    'agent_id' : self.agent,
                    'target' : self.target,
                    'module' : "snmp",
                    'display_name_%s' % self.target :
                        "%s port %s interface stats" % (
                            self.friendly_name, name),
                    'community' : self.community,
            }
            for k in self.metrics:
                metric_names.append(k)
                params["oid_%s" % k] = "%s.%s" % (self.metrics[k], idx)
            params['metric_name'] = metric_names

            for k in sorted(params):
                logging.debug("%20s = %s" % (k, params[k]))

            try:
                rv = self.api.add_check_bundle(**params)
                print "Success"
            except circonusapi.CirconusAPIError, e:
                print "Failed"
                print "   ", e.error
