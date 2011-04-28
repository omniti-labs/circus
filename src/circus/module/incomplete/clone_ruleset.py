__cmdname__ = "clone_ruleset"

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

    def command(self, opts, old_check_id, old_metric_name, new_check_id,
            new_metric_name):
        """Clone rulesets from one check to another

        Arguments:
            old_check_id    -- the check_id to copy the ruleset from
            old_metric_name -- the metric_name to copy the ruleset from
            new_check_id    -- the check_id to copy the ruleset to
            new_metric_name -- the metric_name to copy the ruleset to
        """
        rules = self.api.list_rules(check_id=old_check_id,
                metric_name=old_metric_name)
        for r in rules:
            r['check_id'] = new_check_id
            r['metric_name'] = new_metric_name

        for r in rules:
            log.msgnb("Adding rule %s... " % r['order'])
                log.msgnf("Success")
            except circonusapi.CirconusAPIError, e:
                log.msgnf("Failed")
                log.error(e.error)
                return
        # This code is a stub from the add_rule code - we need to transfer over
        # contact groups when cloning rules
        #for cg in contact_groups:
        #    try:
        #        cg_param = {
        #            'contact_group_id': cg,
        #            'check_id': rule['check_id'],
        #            'metric_name': rule['metric_name'],
        #            'severity': rule['severity']}
        #        rv = self.api.add_rule_contact_group(**cg_param)
