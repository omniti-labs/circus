__cmdname__ = 'delete_graphs'

import json
import re
import sys

import circonusapi
import log
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
        for g in sorted(rv, lambda a, b: cmp(a['title'], b['title'])):
            if re.search(pattern, g['title']):
                filtered_graphs.append(g)
        log.msg("Going to DELETE the following graphs:")
        for g in filtered_graphs:
            log.msg("   ", g['title'])
        if util.confirm():
            for g in filtered_graphs:
                log.msgnb("Deleting %s..." % g['title'])
                try:
                    rv = self.api.remove_graph(graph_id=g['graph_id'])
                    log.msgnf("Success")
                except circonusapi.CirconusAPIError, e:
                    log.msgnf("Failed")
                    log.error(e.error)
