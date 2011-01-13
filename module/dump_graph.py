#!/usr/bin/env python
__cmdname__ = 'dump_graph'
__cmdopts__ = ''

import json
import log
import sys
import uuid

class Module(object):
    def __init__(self, api, account):
        self.api = api

    def command(self, opts, graph_id):
        """Dump the json information for a graph

        This is intended for use when adding graphs via the API. The output is
        given in a format suitable for inclusion into the add_graph api as
        graph_data.

        Arguments:
            graph_id    -- the id of the graph to dump
        """
        try:
            uuid.UUID(graph_id)
        except ValueError:
            log.error("Invalid graph ID specified. It should look like a UUID")
            sys.exit(1)
        rv = self.api.get_graph(graph_id=graph_id)
        # Prettify the returned json before printing
        gd = json.loads(rv['graph_data'])
        print json.dumps(gd, indent=4)
