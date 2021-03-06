# -*- coding: utf-8 -*-
"""
==========
mllib.eval
==========

http://docs.marklogic.com/REST/POST/v1/eval
"""

from __future__ import unicode_literals, print_function, absolute_import

import json

from .restclient import RESTClient
from .utils import KwargsSerializer, ResponseAdapter, dict_pop


class EvalService(RESTClient):
    def eval_post(self, **kwargs):
        requirements = {
            'xquery': '?',
            'javascript': '?',
            'vars': '?',
            'database': '?',
            'txid': '?'
        }
        tool = KwargsSerializer(requirements)
        params, ignored = tool.request_params(kwargs)
        headers = {'Accept': 'multipart/mixed', 'Content-type': 'application/x-www-form-urlencoded'}
        param_names = ('xquery', 'javascript', 'vars', 'database')
        data = {}
        # first source of value is the RESTClient instance (EvalService) eventually overridden by kwargs parameters
        for param in param_names:
            value = getattr(self, param, None)
            if value:
                data[param] = value
        kwargs_data = dict_pop(params, *param_names)
        data.update(kwargs_data)
        if 'vars' in data:
            data['vars'] = json.dumps(dict(data['vars']))
        response = self.rest_post('/v1/eval', params=params, data=data, headers=headers, stream=True)
        return ResponseAdapter(response)
