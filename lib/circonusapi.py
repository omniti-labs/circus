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
            'list_agents': {
                'form_method': 'GET'
            },
            'list_checks': {
                'form_method': 'GET',
                'optional': ['active']
            },
            'list_metrics': {
                'form_method': 'GET',
                'required': ['check_id']
            },
            'add_check_bundle': {
                'form_method': 'POST',
                'required': ['agent_id', 'target', 'metric_name'],
                'optional': ['module', 'period', 'timeout','*']
            },
            'edit_check_bundle': {
                'form_method': 'POST',
                'required': ['bundle_id', 'metric_name', 'period', 'timeout'],
                'optional': ['*']
            },
            'enable_check_bundle': {
                'form_method': 'POST',
                'required': ['bundle_id']
            },
            'disable_check_bundle': {
                'form_method': 'POST',
                'required': ['bundle_id']
            },
            'enable_check': {
                'form_method': 'POST',
                'required': ['check_id']
            },
            'disable_check': {
                'form_method': 'POST',
                'required': ['check_id']
            },
            ### Account management
            'list_accounts': {
                'form_method': 'POST'
            },
            'list_users': {
                'form_method': 'GET',
                'required': ['check_id', 'metric_name']
            },
            'list_contact_groups': {
                'form_method': 'GET'
            },
            'add_contact_group': {
                'form_method': 'POST',
                'required': ['name'],
                'optional': ['agg_window']
            },
            'edit_contact_group': {
                'form_method': 'POST',
                'required': ['contact_group_id'],
                'optional': ['name', 'agg_window']
            },
            'remove_contact_group': {
                'form_method': 'POST',
                'required': ['contact_group_id']
            },
            'add_contact': {
                'form_method': 'POST',
                'required' : ['contact_group_id', 'contact_method'],
                'optional' : ['user_id', 'contact_info']
            },
            'remove_contact': {
                'form_method': 'POST',
                'required': ['contact_group_id'],
                'optional': ['user_id', 'id', 'contact_method']
            },
            ### Rule management
            'list_alerts': {
                'form_method': 'GET',
                'required': ['start', 'end']
            },
            'list_rules': {
                'form_method': 'GET',
                'required': ['check_id', 'metric_name']
            },
            'add_metric_rule': {
                'form_method': 'POST',
                'required': ['check_id', 'metric_name', 'order', 'severity',
                             'value']
            },
            'remove_metric_rule': {
                'form_method': 'POST',
                'required' : ['check_id', 'metric_name', 'order']
            },
            'add_metric_parent': {
                'form_method': 'POST',
                'required' : ['check_id', 'parent_check_id', 'metric_name',
                              'parent_metric_name']
            },
            'remove_metric_parent': {
                'form_method': 'POST',
                'required': ['check_id', 'metric_name']
            },
            'add_rule_contact_group': {
                'form_method': 'POST',
                'required': ['contact_group_id', 'check_id', 'metric_name',
                             'severity']
            },
            'remove_rule_contact_group': {
                'form_method': 'POST',
                'required': ['contact_group_id', 'check_id', 'metric_name',
                             'severity']
            },
            ### Graph management
            'get_graph': {
                'api_method': 'graph',
                'form_method': 'GET',
                'required': ['graph_id']
            },
            'add_graph': {
                'api_method': 'graph',
                'form_method': 'POST',
                'required': ['graph_data']
            },
            'edit_graph': {
                'api_method': 'graph',
                'form_method': 'POST',
                'required': ['graph_id', 'graph_data']
            },
            'remove_graph': {
                'form_method': 'POST',
                'required': ['graph_id']
            },
            'list_graphs': {
                'form_method': 'GET'
            },
            'get_worksheet': {
                'api_method': 'worksheet',
                'form_method': 'GET',
                'required': ['worksheet_id']
            },
            'add_worksheet': {
                'api_method': 'worksheet',
                'form_method': 'POST',
                'required': ['worksheet_data']
            },
            'edit_worksheet': {
                'api_method': 'worksheet',
                'form_method': 'POST',
                'required': ['worksheet_id', 'worksheet_data']
            },
            'remove_worksheet': {
                'form_method': 'POST',
                'required': ['worksheet_id']
            },
            'list_worksheets': {
                'form_method': 'GET'
            }
        }

    def __getattr__(self, name):
        if name in self.methods:
            def f(**parameters):
                # Verify that we passed the right parameters
                required = set(self.methods[name].get('required', []))
                optional = set(self.methods[name].get('optional', []))

                params = set(parameters.keys())
                if not params >= required:
                    raise TypeError("%s requires the following arguments: %s" %
                                    (name, ' '.join(
                                        self.methods[name]['required'])))
                if '*' not in optional and not params <= (required | optional):
                    raise TypeError("Invalid parameters given to %s" % name)

                # Make the api call
                return self.api_call(
                    self.methods[name].get('form_method', 'GET'),
                    self.methods[name].get('api_method', name),
                    **parameters)
            return f
        else:
            raise AttributeError("%s instance has no attribute '%s'" % (
                self.__class__.__name__, name))

    def api_call(self, form_method, method, **parameters):
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
        url = "https://%s/api/json/%s" % (self.hostname, method)
        if form_method == 'POST':
            data = urllib.urlencode(plist)
        elif form_method == 'GET':
            data = None
            url = "%s?%s" % (url, urllib.urlencode(plist))
        req = urllib2.Request(
            url = url, data = data,
            headers = {
                "X-Circonus-Auth-Token" : self.token,
                "X-Circonus-App-Name" : "Circus"
            }
        )
        try:
            fh = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            if e.code == 401:
                raise TokenNotValidated
            if e.code == 403:
                raise AccessDenied
            try:
                data = json.load(e)
            except ValueError:
                data = {}
            raise CirconusAPIError(e.code, data)
        response = json.load(fh)
        fh.close()
        return response

class CirconusAPIException(Exception):
    pass

class TokenNotValidated(CirconusAPIException):
    pass

class AccessDenied(CirconusAPIException):
    pass

class CirconusAPIError(CirconusAPIException):
    def __init__(self, code, data):
        self.code = code
        self.data = data
        self.success = data.get('success', False)
        self.error = data.get('error', '')
