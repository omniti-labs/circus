__cmdname__ = 'compare_hosts'
__cmdopts__ = ''

class Module(object):
    def __init__(self, api, account):
        self.api = api

    def command(self, opts, host1, host2):
        """Compare the metrics of two hosts

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
                    metrics[i][m['name']] = m

        s = []
        for i in range(0, len(ips)):
            s.append(set([j for j in metrics[i] if metrics[i][j]['enabled']]))

        missing = [ s[0] - s[1], s[1] - s[0]]

        if missing[0]:
            print "Metrics present on %s but not on %s:" % (host1, host2)
            for i in missing[0]:
                print "    %s (%s)" % (
                    i, checks[0][metrics[0][i]['check_id']]['name'])

        if missing[1]:
            print "Metrics present on %s but not on %s:" % (host2, host1)
            for i in missing[1]:
                print "    %s (%s)" % (
                    i, checks[1][metrics[1][i]['check_id']]['name'])
