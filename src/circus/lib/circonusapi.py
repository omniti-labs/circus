import json
import urllib
import urllib2
import time


class CirconusAPI(object):

    def __init__(self, token):
        self.hostname = 'circonus.com'
        self.token = token
        # List valid api methods and their parameters here
        # The two lists are required and optional parameters
        self.methods = {
            ### Check management
            'list_agents': {
                'form_method': 'GET'},
            'list_checks': {
                'form_method': 'GET',
                'optional': ['active']},
            'list_metrics': {
                'form_method': 'GET',
                'required': ['check_id']},
            'list_available_metrics': {
                'form_method': 'GET',
                'required': ['check_id']},
            'add_check_bundle': {
                'form_method': 'POST',
                'required': ['agent_id', 'target', 'metric_name'],
                'optional': ['module', 'period', 'timeout', '*']},
            'edit_check_bundle': {
                'form_method': 'POST',
                'required': ['bundle_id', 'metric_name'],
                'optional': ['*']},
            'enable_check_bundle': {
                'form_method': 'POST',
                'required': ['bundle_id']},
            'disable_check_bundle': {
                'form_method': 'POST',
                'required': ['bundle_id']},
            'enable_check': {
                'form_method': 'POST',
                'required': ['check_id']},
            'disable_check': {
                'form_method': 'POST',
                'required': ['check_id']},
            'get_check': {
                'form_method': 'POST',
                'required': ['check_id']},
            'remove_check_bundle': {
                'form_method': 'POST',
                'required': ['bundle_id']},
            ### Account management
            'list_accounts': {
                'form_method': 'POST'},
            'list_users': {
                'form_method': 'GET',
                'required': ['check_id', 'metric_name']},
            'list_contact_groups': {
                'form_method': 'GET'},
            'add_contact_group': {
                'form_method': 'POST',
                'required': ['name'],
                'optional': ['agg_window']},
            'edit_contact_group': {
                'form_method': 'POST',
                'required': ['contact_group_id'],
                'optional': ['name', 'agg_window']},
            'remove_contact_group': {
                'form_method': 'POST',
                'required': ['contact_group_id']},
            'add_contact': {
                'form_method': 'POST',
                'required': ['contact_group_id', 'contact_method'],
                'optional': ['user_id', 'contact_info']},
            'remove_contact': {
                'form_method': 'POST',
                'required': ['contact_group_id'],
                'optional': ['user_id', 'id', 'contact_method']},
            ### Rule management
            #'list_alerts': {
            #    'form_method': 'GET',
            #    'required': ['start', 'end']},
            'list_rules': {
                'form_method': 'GET',
                'optional': ['check_id', 'metric_name']},
            'get_ruleset': {
                'api_method': 'ruleset',
                'form_method': 'GET',
                'optional': ['check_id', 'metric_name']},
            'set_ruleset': {
                'api_method': 'ruleset',
                'form_method': 'POST',
                'required': ['ruleset']},
            #'add_metric_rule': {
            #    'form_method': 'POST',
            #    'required': ['check_id', 'metric_name', 'order', 'severity',
            #                 'value', 'criteria'],
            #    'optional': ['wait']},
            #'remove_metric_rule': {
            #    'form_method': 'POST',
            #    'required': ['check_id', 'metric_name', 'order']},
            'add_metric_parent': {
                'form_method': 'POST',
                'required': ['check_id', 'parent_check_id', 'metric_name',
                              'parent_metric_name']},
            'remove_metric_parent': {
                'form_method': 'POST',
                'required': ['check_id', 'metric_name']},
            'add_rule_contact_group': {
                'form_method': 'POST',
                'required': ['contact_group_id', 'check_id', 'metric_name',
                             'severity']},
            'remove_rule_contact_group': {
                'form_method': 'POST',
                'required': ['contact_group_id', 'check_id', 'metric_name',
                             'severity']},
            'set_metric_notes': {
                'form_method': 'POST',
                'required': ['check_id', 'metric_name'],
                'optional': ['notes', 'link']},
            'list_maintenance': {
                'form_method': 'GET',
                'required': ['start', 'stop'],
                'optional': ['check_id']},
            'add_maintenance': {
                'form_method': 'POST',
                'required': ['check_id', 'metric_name', 'start', 'stop',
                    'severity'],
                'optional': ['notes', 'metric_type']},
            'edit_maintenance': {
                'form_method': 'POST',
                'required': ['maintenance_id', 'start', 'stop']},
            'cancel_maintenance': {
                'form_method': 'POST',
                'required': ['maintenance_id']},
            ### Graph management
            'get_graph': {
                'api_method': 'graph',
                'form_method': 'GET',
                'required': ['graph_id']},
            'add_graph': {
                'api_method': 'graph',
                'form_method': 'POST',
                'required': ['graph_data']},
            'edit_graph': {
                'api_method': 'graph',
                'form_method': 'POST',
                'required': ['graph_id', 'graph_data']},
            'remove_graph': {
                'form_method': 'POST',
                'required': ['graph_id']},
            'list_graphs': {
                'form_method': 'GET'},
            'get_worksheet': {
                'api_method': 'worksheet',
                'form_method': 'GET',
                'required': ['worksheet_id']},
            'add_worksheet': {
                'api_method': 'worksheet',
                'form_method': 'POST',
                'required': ['worksheet_data']},
            'edit_worksheet': {
                'api_method': 'worksheet',
                'form_method': 'POST',
                'required': ['worksheet_id', 'worksheet_data']},
            'remove_worksheet': {
                'form_method': 'POST',
                'required': ['worksheet_id']},
            'list_worksheets': {
                'form_method': 'GET'},
            ### Annotations
            'list_annotations': {
                'form_method': 'GET',
                'optional': ['category', 'start', 'stop']},
            'get_annotation': {
                'api_method': 'annotation',
                'form_method': 'GET',
                'required': ['id']},
            'set_annotation': {
                'api_method': 'annotation',
                'form_method': 'POST',
                'required': ['annotations']},
            'remove_annotation': {
                'form_method': 'POST',
                'required': ['id', 'category'],
                'optional': ['remove_annotations']},
            ### Templates
            'list_templates': {
                'form_method': 'GET'},
            'get_template': {
                'api_method': 'template',
                'form_method': 'GET',
                'required': ['template_id']},
            'set_template': {
                'api_method': 'template',
                'form_method': 'POST',
                'required': ['template_data']},
            'remove_template': {
                'form_method': 'POST',
                'required': ['template_id']}}

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
            demunged_k = k.replace('_dot_', '.')
            if type(parameters[k]) == list:
                for v in parameters[k]:
                    plist.append((demunged_k, v))
            else:
                plist.append((demunged_k, parameters[k]))
        url = "https://%s/api/json/%s" % (self.hostname, method)
        if form_method == 'POST':
            data = urllib.urlencode(plist)
        elif form_method == 'GET':
            data = None
            url = "%s?%s" % (url, urllib.urlencode(plist))
        req = urllib2.Request(url=url, data=data,
            headers={
                "X-Circonus-Auth-Token": self.token,
                "X-Circonus-App-Name": "Circus"})
        for i in range(5):
            # Retry 5 times until we succeed
            try:
                fh = urllib2.urlopen(req)
            except urllib2.HTTPError, e:
                if e.code == 401:
                    raise TokenNotValidated
                if e.code == 403:
                    raise AccessDenied
                if e.code == 429:
                    # We got a rate limit error, retry
                    time.sleep(1)
                    continue
                # Deal with other API errors
                try:
                    data = json.load(e)
                except ValueError:
                    data = {}
                raise CirconusAPIError(e.code, data)
            # We succeeded, exit the for loop
            break
        else:
            # We have been rate limited, retried several times and still got
            # rate limited, so give up and raise an exception.
            raise RateLimitRetryExceeded

        response = json.load(fh)
        # Deal with the unlikely case that we get an error with a 200 return
        # code
        if type(response) == dict and not response.get('success', True):
            raise CirconusAPIError(200, response)
        fh.close()
        return response


class CirconusAPIException(Exception):
    pass


class TokenNotValidated(CirconusAPIException):
    pass


class AccessDenied(CirconusAPIException):
    pass

class RateLimitRetryExceeded(CirconusAPIException):
    pass


class CirconusAPIError(CirconusAPIException):
    """Exception class for any errors thrown by the circonus API.

    Attributes:
        code -- the http code returned
        data -- the json object returned by the API
        success -- whether the request succeeded or failed (this is usually
                    false)
        error -- the error message returned by the API
    """
    def __init__(self, code, data):
        self.code = code
        self.data = data
        if hasattr(data, 'get'):
            self.success = data.get('success', False)
            self.error = data.get('error', '')

    def __str__(self):
        return "HTTP %s - %s" % (self.code, self.error)
