__cmdname__ = "add_worksheet"
__cmdopts__ = "f"
__longopts__ = ["favorite"]

import json
import log
import re
import sys

import graphutil
import util

import circonusapi

class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts, title, pattern):
        """Add a worksheet containing matching graphs

        Arguments:
            pattern         -- a regex to match on graph names

        Options:
            -f/--favorite   -- mark the worksheet as a favorite
        """
        rv = self.api.list_graphs()
        filtered_graphs = []
        for g in sorted(rv, lambda a,b: cmp(a['title'], b['title'])):
            if re.search(pattern, g['title']):
                filtered_graphs.append(g)
        favorite = False
        if ('-f', '') in opts or ('--favorite', '') in opts:
            favorite = True
        worksheet_data = {
            'title': title,
            'favorite': favorite,
            'graphs' : filtered_graphs
        }
        log.msg("Adding a worksheet with the following graphs:")
        for i in filtered_graphs:
            log.msg("    %s" % i['title'])
        if favorite:
            log.msg("Worksheet will be marked as a favorite")
        if not util.confirm():
            log.msg("Not adding worksheet")
            sys.exit(1)
        log.msgnb("Adding worksheet... ")
        try:
            self.api.add_worksheet(worksheet_data=json.dumps(worksheet_data))
            log.msgnf("Success")
        except circonusapi.CirconusAPIError, e:
            log.msgnf("Failed")
            log.error("Unable to add worksheet: %s" % e)
