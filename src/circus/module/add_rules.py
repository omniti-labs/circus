__cmdname__ = "add_rules"

import json
import sys

import circonusapi
import log
import util


class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, template_name, pattern, *params):
        """Adds rules for checks that match the given pattern

        Arguments:
            template_name   -- the name of the template file
            pattern         -- regex to match check names on
            params          -- other parameters (see below)

        Other parameters are specified as "param_name=value" and will
        be substituted in the template. Use {param_name} in the template.

        Some predefined parameters:
            {check_id}     - The check ID
            {check_name}   - The check name
            {check_target} - The target of the check (IP address)
            {check_agent}  - The agent the check is run from
            {groupN}       - Matching groups (the parts in parentheses) in the
                            pattern given on the command line. (replace N with
                            a group number)
        """
        template = util.RuleTemplate(template_name)
        template_params = template.parse_nv_params(params)
        checks, groups = util.find_checks(self.api, pattern)
        util.verify_metrics(self.api, template, checks)
        log.msg("About to add %s rules for the following checks:" % (
            template_name))
        for c in checks:
            log.msg("    %s (%s)" % (c['name'], c['agent']))
        if not util.confirm():
            log.msg("Not adding rules.")
            sys.exit()

        for c in checks:
            p = {
                "check_name":   c['name'],
                "check_id":     c['check_id'],
                "check_target": c['target'],
                "check_agent":  c['agent']}
            p.update(template_params)
            p.update(groups[c['check_id']])
            substituted = template.sub(p)

            # Get mapping from contact group name to ID
            rv = self.api.list_contact_groups()
            contact_group_ids = {}
            for i in rv:
                contact_group_ids[i['name']] = i['contact_group_id']
            for rule in substituted:
                # Extract the contact groups and get the IDs
                for severity in rule['contact_groups']:
                    contact_group_names = rule['contact_groups'][severity]
                    del rule['contact_groups'][severity]
                    rule['contact_groups'][severity] = []
                    for cg in contact_group_names:
                        rule['contact_groups'][severity].append({
                            'id': contact_group_ids[cg],
                            'name': cg
                        })

                log.msgnb("Adding rule for %s... " % c['name'])
                try:
                    rv = self.api.set_ruleset(ruleset=json.dumps(rule))
                    log.msgnf("Success")
                except circonusapi.CirconusAPIError, e:
                    log.msgnf("Failed")
                    log.error(e.error)
