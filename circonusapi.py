import json
import urllib
import urllib2

class CirconusAPI(object):

    def __init__(self, token):
        self.hostname = 'circonus.com'
        self.token = token
        # List valid api methods and their parameters here
        # The two lists are required and optional parameters
        self.methods = {
            ### Check management
            'list_agents':          [['account']],
            'list_checks':          [['account'], ['active']],
            'list_metrics':         [['account', 'check_id']],
            'add_check_bundle':     [['account', 'agent_id', 'target',
                                      'metric_name'],
                                      ['module', 'period', 'timeout','*']],
            'edit_check_bundle':    [['bundle_id', 'metric_name', 'period',
                                      'timeout'], ['*']],
            'enable_check_bundle':  [['bundle_id']],
            'disable_check_bundle': [['bundle_id']],
            'enable_check':         [['check_id']],
            'disable_check':        [['check_id']],
            ### Account Management
            'list_accounts':        [[]],
            'list_users':           [['check_id', 'metric_name']],
            'list_contact_groups':  [['account']],
            'add_contact_group':    [['name'], ['agg_window']],
            'edit_contact_group':   [['contact_group_id'],
                                    ['name', 'agg_window']],
            'remove_contact_group': [['contact_group_id']],
            'add_contact':          [['contact_group_id', 'contact_method'],
                                     ['user_id', 'contact_info']],
            'remove_contact':       [['contact_group_id'],
                                     ['user_id', 'id', 'contact_method']],
            ### Rule Management
            'list_alerts':          [['account', 'start', 'end']],
            'list_rules':           [['account', 'check_id', 'metric_name']],
            'add_metric_rule':      [['account', 'check_id', 'metric_name',
                                      'order', 'severity', 'value']],
            'remove_metric_rule':   [['account', 'check_id', 'metric_name',
                                      'order']],
            'add_metric_parent':    [['check_id', 'parent_check_id',
                                      'metric_name', 'parent_metric_name']],
            'remove_metric_parent': [['check_id', 'metric_name']],
            'add_rule_contact_group': [['contact_group_id', 'check_id',
                                        'metric_name', 'severity']],
            'remove_rule_contact_group': [['contact_group_id', 'check_id',
                                        'metric_name', 'severity']]
        }

    def __getattr__(self, name):
        if name in self.methods:
            def f(**parameters):
                # Verify that we passed the right parameters
                required = set(self.methods[name][0])
                try:
                    optional = set(self.methods[name][1])
                except IndexError:
                    optional = set()

                params = set(parameters.keys())
                if not params >= required:
                    raise TypeError("%s requires the following arguments: %s" %
                                    (name, ' '.join(self.methods[name][0])))
                if '*' not in optional and not params <= (required | optional):
                    raise TypeError("Invalid parameters given to %s" % name)

                # Make the api call
                return self.api_call(name, **parameters)
            return f
        else:
            raise AttributeError("%s instance has no attribute '%s'" % (
                self.__class__.__name__, name))

    def api_call(self, method, **parameters):
        """Performs a circonus api call.

        Post is always used, even for read only requests. The api says that
        post is always valid, so there is no need to decide if something is
        read/write and setting get/post appropriately
        """

        # Convert list to multiple values
        # i.e. "a" : [1,2,3] to (eventually) a=1&a=2&a=3
        plist = []
        for k in parameters:
            if type(parameters[k]) == list:
                for v in parameters[k]:
                    plist.append((k,v))
            else:
                plist.append((k, parameters[k]))

        req = urllib2.Request(
            "https://%s/api/json/%s" % (self.hostname, method),
            headers = {
                "X-Circonus-Auth-Token" : self.token,
                "X-Circonus-App-Name" : "Circus"
            }
        )
        try:
            fh = urllib2.urlopen(req, urllib.urlencode(plist))
        except urllib2.HTTPError, e:
            if e.code == 401:
                raise TokenNotValidated
            if e.code == 403:
                raise AccessDenied
            raise
        response = json.load(fh)
        fh.close()
        return response

class CirconusAPIException(Exception):
    pass

class TokenNotValidated(CirconusAPIException):
    pass

class AccessDenied(CirconusAPIException):
    pass
