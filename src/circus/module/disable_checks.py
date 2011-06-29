#!/usr/bin/env python
__cmdname__ = 'disable_checks'
__cmdopts__ = 'd'

import log
import util

class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, pattern):
        """Disable check bundles based on pattern

        Note: if you want to disable only some metrics for a check, use the
        disable_metrics command instead.

        Arguments:
            pattern     --  search pattern for checks
        """
        checks, groups = util.find_checks(self.api, pattern)
        if not checks:
            log.error("No matching checks found\n" % check_id)
            return

        print "Disabling the following check bundles: "
        bundle_ids = {}
        for c in checks:
            if c['bundle_id'] not in bundle_ids:
                print "    %s" % c['name']
                bundle_ids[c['bundle_id']] = c['name']

        if util.confirm():
            for c in bundle_ids:
                log.msg("Disabling %s" % bundle_ids[c])
                self.api.disable_check_bundle(bundle_id=c)
