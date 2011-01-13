#!/usr/bin/env python
__cmdname__ = 'enable_metrics'
__cmdopts__ = 'e'

import log

class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, check_id):
        """List inactive metrics, optionally enabling them

        Options:
            -e - enable the metrics

        Arguments:
            check_id    --  Which check to list metrics for
        """
        rv = self.api.list_checks()
        check = None
        for c in rv:
            if str(c['check_id']) == check_id:
                check = c
        if not check:
            log.error("Check %s not found\n" % check_id)
            return
        rv = self.api.list_metrics(check_id = check_id)
        to_enable = []
        already_enabled = []
        print "Disabled Metric List for check %s (%s)" % (
            check_id, check['name'])
        for metric in sorted(rv):
            if metric['enabled'] == False:
                print "    %s" % metric['name']
                print metric
                to_enable.append(metric['name'])
            else:
                already_enabled.append(metric['name'])
        if not to_enable:
            print "    No disabled metrics"

        if ('-e', '') in opts:
            # Enable metrics here
            self.api.edit_check_bundle(
                bundle_id=check['bundle_id'],
                metric_name = already_enabled + to_enable)
