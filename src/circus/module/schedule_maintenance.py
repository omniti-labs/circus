__cmdname__ = 'schedule_maintenance'

import re
import sys

import circonusapi
import util
import log


class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, duration, pattern, notes=""):
        """Schedule maintenance for rules matching the pattern

        Arguments:
            duration -- how long should the maintenance window last?
            pattern  -- pattern to match the check name with
            notes    -- optional notes for the maintenance window

        Duration should be of the form <integer>[m|h|d]. Examples:
            10m == 10 minutes
            4h  == 4 hours
            2d  == 2 days
        """
        if duration[-1] not in 'mhd':
            log.error("Duration needs to be of the form <integer>[m|h|d]")
            sys.exit(1)
        rules = self.api.list_rules()
        checks = self.api.list_checks(active='true')
        filtered_checks = {}
        for c in checks:
            if re.search(pattern, c['name'], flags=re.IGNORECASE):
                filtered_checks[c['check_id']] = c
        filtered_rules = [r for r in rules if r['check_id'] in
                filtered_checks]
        # Remove duplicates
        dedup_rules = {}
        for r in filtered_rules:
            dedup_rules[(r['check_id'], r['metric_name'], r['severity'])] = r
        filtered_rules = dedup_rules.values()
        log.msg("Scheduling maintenance for:")
        for r in sorted(filtered_rules):
            print "    Sev %s : %s : %s (from %s)" % (
                    r['severity'],
                    filtered_checks[r['check_id']]['name'],
                    r['metric_name'],
                    filtered_checks[r['check_id']]['agent'])
        if util.confirm():
            log.msg("Setting maintenance:")
            for r in filtered_rules:
                log.msgnb("Sev %s : %s : %s..." % (
                        r['severity'],
                        filtered_checks[r['check_id']]['name'],
                        r['metric_name']))
                try:
                    self.api.add_maintenance(
                        check_id=r['check_id'],
                        start='now',
                        stop=duration,
                        metric_name=r['metric_name'],
                        severity=r['severity'],
                        notes=notes)
                    log.msgnf("Success")
                except circonusapi.CirconusAPIError, e:
                    log.msgnf("Failed")
                    log.error(e.error)
