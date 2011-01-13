__cmdname__ = 'rename_graphs'

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

    def command(self, opts, pattern, replacement):
        """Rename multiple graphs at once

        Arguments:
            pattern     -- a regex to select the graphs to rename
            replacement -- what to replace the graph name with

        The replacement can contain \1, \2 etc. to refer to groups in the
        pattern.
        """
        rv = self.api.list_graphs()
        filtered_graphs = []
        for g in sorted(rv, lambda a,b: cmp(a['title'], b['title'])):
            if re.search(pattern, g['title']):
                filtered_graphs.append(g)
        renames = {}
        log.msg("Going to perform the following renames:")
        for g in filtered_graphs:
            renames[g['title']] = re.sub(pattern, replacement, g['title'])
            log.msg("    %s => %s" % (g['title'], renames[g['title']]))
        if util.confirm():
            for g in filtered_graphs:
                log.msgnb("Renaming %s..." % g['title'])
                try:
                    rv = self.api.get_graph(
                        graph_id=g['graph_id'])
                except circonusapi.CirconusAPIError, e:
                    log.msgnf("Failed to fetch current graph")
                    log.error(e.error)
                    continue
                try:
                    graph_data = json.loads(rv['graph_data'])
                except KeyError:
                    log.msgnf("Failed to fetch current graph")
                    log.error("No graph data returned")
                    continue
                except ValueError:
                    log.msgnf("Failed to fetch current graph")
                    log.error("Unable to parse the graph data")
                    continue
                graph_data['title'] = renames[g['title']]
                try:
                    rv = self.api.edit_graph(graph_id=g['graph_id'],
                                             graph_data=json.dumps(graph_data))
                    log.msgnf("Success")
                except circonusapi.CirconusAPIError, e:
                    log.msgnf("Failed to edit graph")
                    log.error(e.error)
