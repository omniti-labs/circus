__cmdname__ = "add_check"

import json
import os
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
        template_dir=os.path.join(os.path.dirname(__file__),
                                  "..", "templates", "check")
        template = util.Template(template_name, template_dir)
        targetip = util.resolve_target(target)
        template_params = {
            'agent': agent,
            'target': target,
            'targetip': targetip
        }
        for param in params:
            try:
                name, value = param.split('=', 1)
            except ValueError:
                log.error("Invalid parameter: %s" % param)
                log.error("Extra parameters must be specified as name=value")
                sys.exit(1)
            template_params[name] = value

        substituted = template.sub(template_params)
        # Add required parameters
        substituted['agent_id'] = util.get_agent(self.api, agent)
        substituted['target'] = targetip

        try:
            self.api.add_check_bundle(**substituted)
            log.msg("Check added")
        except CirconusError, e:
            log.error("Failed to add check: ", e.error)
