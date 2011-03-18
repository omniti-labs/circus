__cmdname__ = 'dump_rules'

import re
import json

import circonusapi
import log


class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts):
        """Dump all rules on an account in json format

        The aim for this command is to be able to 'back up' rules for later
        importing.
        """
        rules = self.api.list_rules()
        # Hack to prettify the json
        print json.dumps(rules, indent=4)
