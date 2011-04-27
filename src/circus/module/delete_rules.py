__cmdname__ = "delete_rules"

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

    def command(self, opts, check_pattern, metric_pattern=None):
        """Removes rules for checks that match the given pattern

        Arguments:
            check_pattern   -- regex to match check names on (optional)
            metric_pattern  -- regex to match metric names on (optional)

        At least one of check_pattern or metric_pattern must be provided. If
        you want to leave out the check_pattern, then specify it as an empty
        string.
        """
        rules = self.api.list_rules()

        if check_pattern and check_pattern != '.':
            checks, groups = util.find_checks(self.api, check_pattern)
            check_ids = dict([(c['check_id'], c['name']) for c in checks])
            matching = [r for r in rules if r['check_id'] in check_ids]
        else:
            checks = self.api.list_checks()
            check_ids = dict([(c['check_id'], c['name']) for c in checks])
            matching = rules

        if metric_pattern:
            matching = [r for r in matching if
                    re.search(metric_pattern, r['metric_name'])]

        matching = sorted(matching, reverse=True,
                key=lambda x: (x['check_id'], x['metric_name'], x['order']))
        log.msg("About to delete the following rules:")
        for r in matching:
            log.msg("%s`%s (%s - %s %s)" % (check_ids[r['check_id']],
                r['metric_name'], r['order'], r['criteria'], r['value']))
        if util.confirm():
            for r in matching:
                log.msgnb("Deleting %s`%s (%s)..." % (
                    check_ids[r['check_id']], r['metric_name'], r['order']))
                try:
                    rv = self.api.remove_metric_rule(check_id=r['check_id'],
                            metric_name=r['metric_name'], order=r['order'])
                    log.msgnf("Success")
                except circonusapi.CirconusAPIError, e:
                    log.msgnf("Failed")
                    log.error(e.error)
        else:
            log.msg("Not deleting rules")
