#!/usr/bin/env python
__cmdname__ = 'activate_metrics'
__cmdopts__ = ''

import sys

import log
import util

class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, pattern, *metrics_to_enable):
        """Activate metrics for checks

        Arguments:
            pattern             -- Pattern for checks
            metrics_to_enable   -- List of metrics to enable
        """
        checks, groups = util.find_checks(self.api, pattern)
        already_enabled = {}

        # Pick only one check per check bundle
        bundles = {}
        for c in checks:
            if c['bundle_id'] in bundles:
                continue
            bundles[c['bundle_id']] = c

        log.msg("Retrieving metrics for checks")
        count = 0
        for c in bundles.values():
            count += 1
            print "\r%s/%s" % (count, len(bundles)),
            sys.stdout.flush()
            rv = self.api.list_metrics(check_id=c['check_id'])
            already_enabled[c['check_id']] = []
            for metric in sorted(rv):
                if metric['enabled']:
                    already_enabled[c['check_id']].append(metric['name'])

        log.msg("Metrics to enable: %s" % (', '.join(metrics_to_enable)))
        log.msg("About to enable metrics for the following checks")
        for c in bundles.values():
            log.msg("    %s (%s)" % (c['name'],
                ', '.join(already_enabled[c['check_id']])))

        if util.confirm():
            for c in bundles.values():
                # Enable metrics here
                log.msgnb("%s..." % c['name'])
                all_metrics = set(already_enabled[c['check_id']]) \
                    | set(metrics_to_enable)
                if all_metrics != set(already_enabled[c['check_id']]):
                    # The set of metrics has changed, apply the edit
                    self.api.edit_check_bundle(
                        bundle_id=c['bundle_id'],
                        metric_name=list(all_metrics))
                    log.msgnf("Done")
                else:
                    log.msgnf("No changes")
