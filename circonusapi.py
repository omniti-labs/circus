import json
import urllib
import urllib2

class CirconusAPI(object):

    def __init__(self, email, password):
        self.hostname = 'circonus.com'
        self.email = email
        self.password = password
        # List valid api methods and their parameters here
        # The two lists are required and optional parameters
        self.methods = {
            ### Check management
            'list_agents':          [['email', 'password', 'account']],
            'list_checks':          [['email', 'password', 'account'],
                                     ['active']],
            'list_metrics':         [['email', 'password', 'account',
                                      'check_id']],
            # TODO - allow anything as an optional item
            'add_check_bundle':     [['email', 'password', 'account',
                                      'agent_id', 'target', 'metric_name',
                                      'module', 'period', 'timeout']],
            'edit_check_bundle':    [['email', 'password', 'bundle_id',
                                      'metric_name', 'period', 'timeout']],
            'enable_check_bundle':  [['email', 'password', 'bundle_id']],
            'disable_check_bundle': [['email', 'password', 'bundle_id']],
            'enable_check':         [['email', 'password', 'check_id']],
            'disable_check':        [['email', 'password', 'check_id']],
            ### Account Management
            'list_accounts':        [['email', 'password']],
            'list_users':           [['email', 'password', 'check_id',
                                      'metric_name']],
            'list_contact_groups':  [['email', 'password', 'account']],
            'add_contact_group':    [['name'], ['agg_window']],
            'edit_contact_group':   [['contact_group_id'],
                                    ['name', 'agg_window']],
            'remove_contact_group': [['contact_group_id']],
            'add_contact':          [['contact_group_id', 'contact_method'],
                                     ['user_id', 'contact_info']],
            'remove_contact':       [['contact_group_id'],
                                     ['user_id', 'id', 'contact_method']],
            ### Rule Management
            'list_alerts':          [['email', 'password', 'account',
                                      'start', 'end']],
            'list_rules':           [['email', 'password', 'account',
                                      'check_id', 'metric_name']],
            'add_metric_rule':      [['email', 'password', 'account',
                                      'check_id', 'metric_name', 'order',
                                      'severity', 'value']],
            'remove_metric_rule':   [['email', 'password', 'account',
                                      'check_id', 'metric_name', 'order']],
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

                # Automatically fill in email/password if required
                if 'email' in required and 'email' not in parameters:
                    parameters['email'] = self.email
                if 'password' in required and 'password' not in parameters:
                    parameters['password'] = self.password

                params = set(parameters.keys())
                if not params >= required or \
                   not params <= (required | optional):
                    raise TypeError("%s requires the following arguments: %s" %
                                    (name, ' '.join(self.methods[name][0])))
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
        fh = urllib2.urlopen("https://%s/api/json/%s" % (
            self.hostname, method),
            urllib.urlencode(parameters))
        response = json.load(fh)
        fh.close()
        return response
