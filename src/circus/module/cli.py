__cmdname__ = 'cli'

import code


class Module(object):
    def __init__(self, api, account):
        self.api = api
        self.account = account

    def command(self, opts):
        """Start a python CLI with access to the Circonus API.

        This allows you to run api commands interactively. Access the api with
        self.api. For example: self.api.list_checks(active='active').

        Look at the circonusapi module for information on accessing the API.
        """
        banner = "Circus interpreter (python cli)\n" \
                "use self.api to access the circonus api"
        code.interact(banner=banner, local=locals())
