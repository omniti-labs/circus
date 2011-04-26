__cmdname__ = "delete_rules"

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

    def command(self, opts, pattern):
        """Removes rules for checks that match the given pattern

        Arguments:
            pattern         -- regex to match check names on
        """
        checks, groups = util.find_checks(self.api, pattern)
        check_ids = dict([(c['check_id'], c['name']) for c in checks])
        rules = self.api.list_rules()
        matching = [r for r in rules if r['check_id'] in check_ids]
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
