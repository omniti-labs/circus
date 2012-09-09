#!/usr/bin/env python
__cmdname__ = 'disable_metrics'
__cmdopts__ = 'd'

import log
import util

class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, check_pattern, metric_pattern):
        """List active metrics, optionally disabling them

        Note: if you want to disable all metrics for a check, use the
        disable_checks command instead.

        Options:
            -d - disable the metrics

        Arguments:
            check_pattern     --  search pattern for checks
            metric_pattern    --  search pattern for metrics
        """
        checks, groups = util.find_checks(self.api, check_pattern)
        if not checks:
            log.error("No matching checks found\n" % check_id)
            return
        to_remove = {}
        to_keep = {}
        check_names = {}
        bundle_names = {}
        for c in checks:
            check_names[c['check_id']] = c['name']
            bundle_names[c['bundle_id']] = c['name']
            matching_metrics, non_matching_metrics = util.find_metrics(
                    self.api, c['check_id'], metric_pattern)
            if matching_metrics:
                to_remove[c['check_id']] = matching_metrics
                to_keep[c['bundle_id']] = non_matching_metrics

        print "Disabling the following metrics: "
        for c in sorted(to_remove):
            print "    %s" % check_names[c]
            for m in to_remove[c]:
                print "        %s" % m['name']

        if ('-d', '') in opts:
            if util.confirm():
                for c in to_keep:
                    log.msg("Disabling metrics for check: %s" %
                            bundle_names[c])
                    self.api.edit_check_bundle(bundle_id=c,
                            metric_name=[i['name'] for i in to_keep[c]])
