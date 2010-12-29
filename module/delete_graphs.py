__cmdname__ = 'delete_graphs'

import json
import re
import sys

import circonusapi
import util

class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, pattern):
        """Delete multiple graphs at once

        Arguments:
            pattern     -- a regex to select the graphs to delete
        """
        rv = self.api.list_graphs()
        filtered_graphs = []
        for g in sorted(rv, lambda a,b: cmp(a['title'], b['title'])):
            if re.search(pattern, g['title']):
                filtered_graphs.append(g)
        print "Going to DELETE the following graphs:"
        for g in filtered_graphs:
            print "   ", g['title']
        if util.confirm():
            for g in filtered_graphs:
                print "Deleting %s..." % g['title'],
                sys.stdout.flush()
                try:
                    rv = self.api.remove_graph(graph_id=g['graph_id'])
                    print "Success"
                except circonusapi.CirconusAPIError, e:
                    print "Failed"
                    print "   ", e.error
