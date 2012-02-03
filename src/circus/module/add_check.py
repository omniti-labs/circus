__cmdname__ = "add_check"

import json
import os
import re
import sys

import circonusapi
import log
import util


class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, template_name, target, agent, *params):
        """Adds a check based on a template

        Arguments:
            template_name   -- the name of the template file
            check_name      -- the name for the check
            target          -- the target of the check (can be a hostname)
            agent           -- the agent to run the check from
            params          -- other parameters (see below)

        Other parameters are specified as "param_name=value" and will
        be substituted in the template. Use {param_name} in the template.

        Some predefined parameters:

            {agent}         -- the agent provided on the command line
            {target}        -- the target provided on the command line
            {targetip}      -- the ip of the target resolved in dns
                               (may be same as target if target was provided
                                as an IP)
        """
        template = util.Template(template_name, "check")
        targetip = util.resolve_target(target)
        template_params = {
            'agent': agent,
            'target': target,
            'targetip': targetip}
        template_params.update(template.parse_nv_params(params))

        substituted = template.sub(template_params)
        # Add required parameters
        substituted['agent_id'] = util.get_agent(self.api, agent)
        substituted['target'] = targetip

        # Allow matching metrics by regex, find available metrics, and test
        # them against each regex in the metrics_regex key in the template to
        # see if they match.
        if 'metric_regex' in substituted:
            log.msg("Fetching available metrics for regex match")
            try:
                substituted['test_mode'] = 1
                rv = self.api.add_check_bundle(**substituted)
                del substituted['test_mode']
            except circonusapi.CirconusAPIError, e:
                log.error("Failed to fetch available metrics: %s" % e.error)
                sys.exit(1)
            available_metrics = rv['metrics']
            for metric_type in available_metrics:
                for m in available_metrics[metric_type]:
                    for regex in substituted['metric_regex']:
                        if re.match(regex, m):
                            substituted['metric_name'].append(m)
                            break
            log.msg("Metrics to include in the check:")
            for m in sorted(substituted['metric_name']):
                print "    %s" % m

        try:
            self.api.add_check_bundle(**substituted)
            log.msg("Check added")
        except circonusapi.CirconusAPIError, e:
            log.error("Failed to add check: %s" % e.error)
