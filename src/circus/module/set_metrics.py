#!/usr/bin/env python
__cmdname__ = 'set_metrics'
__cmdopts__ = ''

import re
import sys

import log
import util

class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, pattern, *metrics_to_enable):
        """Set the active metrics for a check based on regular expression

        This command will set the enabled metrics to exactly what matches the
        pattern(s) given. Any other metrics will be disabled, regardless of
        what their original setting was.

        Arguments:
            pattern             -- Pattern for checks
            metrics_to_enable   -- One or more regexes for enabled metrics
        """
        checks, groups = util.find_checks(self.api, pattern)
        to_enable = {}

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
            metrics = self.api.list_metrics(check_id=c['check_id'])
            to_enable[c['check_id']] = []
            for metric in sorted(metrics):
                for pattern in metrics_to_enable:
                    if re.match(pattern, metric['name']):
                        to_enable[c['check_id']].append(metric['name'])

        log.msg("About to set enabled metrics for the following checks")
        for c in bundles.values():
            log.msg("    %s (%s)" % (c['name'],
                ', '.join(to_enable[c['check_id']])))

        if util.confirm():
            for c in bundles.values():
                # Enable metrics here
                log.msgnb("%s..." % c['name'])
                # The set of metrics has changed, apply the edit
                self.api.edit_check_bundle(
                    bundle_id=c['bundle_id'],
                    metric_name=to_enable[c['check_id']])
                log.msgnf("Done")
