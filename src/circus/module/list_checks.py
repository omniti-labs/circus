__cmdname__ = 'list_checks'
__cmdopts__ = 'la'

import re

class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, pattern=''):
        """List the checks for an account

        Options:
            -l - Long listing (include extra information)
            -a - Include inactive and deleted checks also

        Arguments:
            pattern --  A regex to filter which checks are returned
        """
        active = 'true'
        if ('-a', '') in opts:
            active = ''
        rv = self.api.list_checks(active=active)
        if pattern:
            filtered_checks = []
            for c in rv:
                if re.search(pattern, c['name']):
                    filtered_checks.append(c)
        else:
            filtered_checks = rv
        print "Check List for %s" % self.account
        for check in sorted(filtered_checks):
            check_active = ''
            if check['active'] == 'false':
                check_active = ' (inactive)'
            if check['active'] == 'deleted':
                check_active = ' (deleted)'
            print "    %s%s" % (check['name'], check_active)
            if ('-l', '') in opts:
                print "        Agent: %s, Type: %s" % (check['agent'],
                                                   check['type'])
                print "        Bundle Id: %s, Check Id: %s" % (
                    check['bundle_id'], check['check_id'])
                print "        Last modified by: %s on %s" % (
                    check['last_modified_by'], check['last_modified'])
