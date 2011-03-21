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
            params          -- Search/replace on datapoint values

        The search/replace parameters will replace any datapoint values,
        including the check_id, metric_name, colors, and datapoint names.
        Parameters should be of the form:

        search_term=replacement

        For example, to modify the check id, you can do 1234=2345

        You can also specify a single number without an equals sign. In this
        case, all check ids that aren't replaced with another pattern will be
        set to this value.

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

        subs = {}
        default_check_id = None
        for p in params:
            try:
                # First try to parse as a single check id
                default_check_id = int(p)
                continue
            except ValueError:
                pass
            parts = [i for i in p.split('=', 1)]
            try:
                subs[parts[0]] = parts[1]
            except IndexError:
                log.error("Invalid substitution: %s" % p)
                sys.exit(1)

        for d in graph_data['datapoints']:
            for k in d:
                if type(d[k]) == str or type(d[k]) == unicode:
                    # String search/replace
                    for s in subs:
                        d[k] = d[k].replace(s, subs[s])
                        print d[k], s, subs[s]
                elif type(d[k]) == int:
                    # Integer replacement (matches only on the whole number)
                    # Used for check_ids
                    if str(d[k]) in subs:
                        d[k] = int(subs[str(d[k])])
                    elif k == 'check_id' and default_check_id:
                        # If we didn't do a substitution previously, and we're
                        # considering a check_id, replace the check_id with
                        # the default
                        d[k] = default_check_id

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
