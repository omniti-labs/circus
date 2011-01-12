"""Miscellaneous graph utilities"""
import json
import os
import os.path
import re

template_dir=os.path.join(os.path.dirname(__file__), "..", "templates",
                          "graph")

class Template(object):
    def __init__(self, name):
        with open(os.path.join(template_dir, "%s.json" % name)) as fh:
            self.template = json.load(fh)

    def sub(self, params):
        """Substitute parameters in the graph template"""
        return self._process(self.template, params)

    def get_metrics(self):
        """Returns a list of metrics specified in the graph template"""
        return [{
            'name': i['metric_name'],
            'type': i['metric_type']
        } for i in self.template['datapoints']]

    def _process(self, i, params):
        if type(i) == dict:
            return self._process_dict(i, params)
        if type(i) == list:
            return self._process_list(i, params)
        if type(i) == str or type(i) == unicode:
            return self._process_str(i, params)
        return i

    def _process_dict(self, d, params):
        new_d = {}
        for k, v in d.items():
            new_d[k] = self._process(v, params)
        return new_d

    def _process_list(self, l, params):
        new_l = []
        for i in l:
            new_l.append(self._process(i, params))
        return new_l

    def _process_str(self, s, params):
        # Special case the check_id - make it an integer if it's the only
        # thing present in the string
        if s == "{check_id}":
            return int(params['check_id'])
        return re.sub("{(\S+)}", lambda m: params[m.group(1)], s)
