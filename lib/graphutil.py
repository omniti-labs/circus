"""Miscellaneous graph utilities"""
import json
import os
import os.path
import re

template_dir=os.path.join(os.path.dirname(__file__), "..", "templates")

class Template(object):
    def __init__(self, name):
        with open(os.path.join(template_dir, "%s.json" % name)) as fh:
            self.template = json.load(fh)

    def sub(self, params):
        """Substitute parameters in the graph template"""
        return self._process(self.template, params)

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
        # Custom templating for number types - if the formatting is for a
        # single number, return that number and don't format as string
        m = re.match("%\((\S+)\)d", s)
        if m:
            return int(params[m.group(1)])
        # Otherwise, use standard python templating
        return s % params
