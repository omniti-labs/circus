__cmdname__ = 'compare_hosts'
__cmdopts__ = ''

import collections

class recursivedefaultdict(collections.defaultdict):
    def __init__(self):
        self.default_factory = type(self)

class Module(object):
    def __init__(self, api, account):
        self.api = api

    def command(self, opts, host1, host2):
        """Compare the metrics of two hosts

        Arguments:
            host1   --  The first host to compare
            host2   --  The host to compare it with
        """
        rv = self.api.list_checks()
        ips = [host1, host2]

        # Fetch checks first
        checks = [{}, {}]
        for check in rv:
            for i in range(0, len(ips)):
                if check['target'] == ips[i]:
                    checks[i][check['check_id']] = check
                    continue

        # Then metrics
        metrics = [{}, {}]
        for i in range(0, len(ips)):
            for check in checks[i]:
                # TODO - agents
                rv = self.api.list_metrics(check_id=check)
                for m in rv:
                    metrics[i]["%s`%s" % (m['check_id'], m['name'])] = m

        s = [] # Sets to compare
        # Mapping from metric name/type/agent to check name
        check_names = recursivedefaultdict()
        for i in range(0, len(ips)):
            tmp = []
            for metric_id, m in metrics[i].items():
                if m['enabled']:
                    c = checks[i][m['check_id']]
                    # The set will compare all of the criteria below
                    tmp.append((m['name'], c['type'], c['agent']))
                    check_names[c['agent']][c['type']][m['name']] = c['name']
            s.append(set(tmp))

        missing = [ s[0] - s[1], s[1] - s[0]]

        if missing[0]:
            print "Metrics present on %s but not on %s:" % (host1, host2)
            for i in missing[0]:
                print "    %s (%s/%s/%s)" % (
                    i[0], i[1], i[2], check_names[i[2]][i[1]][i[0]])

        if missing[1]:
            print "Metrics present on %s but not on %s:" % (host2, host1)
            for i in missing[1]:
                print "    %s (%s/%s/%s)" % (
                    i[0], i[1], i[2], check_names[i[2]][i[1]][i[0]])
