"""Miscellaneous graph utilities"""
import json
import os
import os.path
import re

import util

template_dir=os.path.join(os.path.dirname(__file__), "..", "templates",
                          "graph")

class Template(util.Template):
    def __init__(self, name):
        super(Template, self).__init__(name, template_dir)

    def get_metrics(self):
        """Returns a list of metrics specified in the graph template"""
        return [{
            'name': i['metric_name'],
            'type': i['metric_type']
        } for i in self.template['datapoints']]

    def _process_str(self, s, params):
        # Special case the check_id - make it an integer if it's the only
        # thing present in the string
        if s == "{check_id}":
            return int(params['check_id'])
        return super(Template, self)._process_str(s, params)
