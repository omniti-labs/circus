__cmdname__ = "copy_graph"
__cmdopts__ = "v"

import json
import log
import sys
import uuid

import util

import circonusapi


class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, graph_id, new_title, *params):
        """Copy a graph, changing some parameters

        Options:
            -v              -- Show the new graph data before adding the graph

        Arguments:
            graph_id        -- The UUID of the graph you want to copy
            new_title       -- The title of the new graph
            params          -- Old -> New check_id mapping

        Check_id mapping should be of the form oldid=newid. For example:
        1234=2345.

        You can also specify a check_id mapping as a single number without an
        equals sign. In this case, all other check ids that aren't part of the
        mapping will be changed to this value.

        If you have a graph that is only for a single check, then specifying
        the check id mapping as a single number is what you want.
        """
        try:
            uuid.UUID(graph_id)
        except ValueError:
            log.error("Invalid graph ID specified. It should look like a UUID")
            sys.exit(1)
        rv = self.api.get_graph(graph_id=graph_id)
        graph_data = json.loads(rv['graph_data'])

        # Set the new title
        graph_data['title'] = new_title

        check_id_mapping = {}
        default_check_id = None
        for p in params:
            try:
                parts = [int(i) for i in p.split('=', 1)]
            except ValueError:
                log.error("Invalid check_id mapping: %s" % p)
                sys.exit(1)
            try:
                check_id_mapping[parts[0]] = parts[1]
            except IndexError:
                default_check_id = parts[0]

        for d in graph_data['datapoints']:
            if d['check_id'] in check_id_mapping:
                d['check_id'] = check_id_mapping[d['check_id']]
            elif default_check_id:
                d['check_id'] = default_check_id

        if ('-v', '') in opts:
            print json.dumps(graph_data, indent=4)
            if not util.confirm():
                log.msg("Not adding graph.")
                sys.exit(0)

        log.msgnb("Adding copied graph: %s..." % graph_data['title'])
        try:
            rv = self.api.add_graph(graph_data=json.dumps(graph_data))
            log.msgnf("Success")
        except circonusapi.CirconusAPIError, e:
            log.msgnf("Failed")
            log.error(e.error)
