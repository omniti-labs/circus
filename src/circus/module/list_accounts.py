#!/usr/bin/env python
__cmdname__ = 'list_accounts'
__cmdopts__ = 'l'


class Module(object):
    def __init__(self, api, account):
        self.api = api

    def command(self, opts):
        """List the accounts you have access to.

        Please note that each account needs a separate API token.

        Options:
            -l - Long listing (show metric count)
        """
        rv = self.api.list_accounts()
        print "Account List"
        for account in sorted(rv):
            desc = ""
            if account['account_description']:
                desc = " (%s)" % account['account_description']
            print "    %s%s" % (account['account_name'], desc)
            if ('-l', '') in opts:
                print "        Circonus metrics:   %s/%s" % (
                    account['circonus_metrics_used'],
                    account['circonus_metric_limit'])
                if 'enterprise_metric_limit' in account:
                    print "        Enterprise metrics: %s/%s" % (
                        account['enterprise_metrics_used'],
                        account['enterprise_metric_limit'])
