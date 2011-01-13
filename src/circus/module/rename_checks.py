__cmdname__ = 'rename_checks'
__cmdopts__ = 'a'

import re
import sys

import circonusapi
import util
import log

class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, pattern, replacement):
        """Rename multiple checks at once

        Options:
            -a - Include inactive and deleted checks also

        Arguments:
            pattern     -- a regex to select the checks to rename
            replacement -- what to replace the check name with

        The replacement can contain \1, \2 etc. to refer to groups in the
        pattern.
        """
        active = 'true'
        if ('-a', '') in opts:
            active = ''
        rv = self.api.list_checks(active=active)
        filtered_checks = []
        # We rename bundles, not checks, so only do each bundle once
        bundles = {}
        for check in sorted(rv):
            if re.search(pattern, check['name']):
                if not bundles.has_key(check['bundle_id']):
                    filtered_checks.append(check)
                    bundles[check['bundle_id']] = True
        renames = {}
        log.msg("Going to perform the following renames:")
        for c in filtered_checks:
            renames[c['name']] = re.sub(pattern, replacement, c['name'])
            log.msg("%s => %s" % (c['name'], renames[c['name']]))
        if util.confirm():
            for c in filtered_checks:
                log.msgnb("Renaming %s... " % c['name'])
                metrics = [m['name'] for m in
                           self.api.list_metrics(check_id=c['check_id'])]
                params = {
                    'bundle_id': c['bundle_id'],
                    'metric_name': metrics,
                    'display_name_%s' % c['target']: renames[c['name']]
                }
                try:
                    rv = self.api.edit_check_bundle(**params)
                    log.msgnf("Success")
                except circonusapi.CirconusAPIError, e:
                    log.msgnf("Failed")
                    log.error(e.error)
