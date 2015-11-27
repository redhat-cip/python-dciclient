# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from prettytable import PrettyTable

import click
import json
import six


def flatten(d, prefix=''):
    ret = []
    for k, v in d.items():
        p = k if not prefix else prefix + '.' + k
        if isinstance(v, dict):
            ret += flatten(v, prefix=p)
        else:
            ret.append("%s=%s" % (p, v))
    return ret


def print_json(result_json):
    formatted_result = json.dumps(result_json, indent=4)
    click.echo(formatted_result)


def print_prettytable(data, headers):
    DEFAULT_HEADERS = ['Property', 'Value']
    headers = headers or DEFAULT_HEADERS
    table = PrettyTable(headers)

    if headers == DEFAULT_HEADERS:
        for item in sorted(six.iteritems(data)):
            table.add_row(item)
    else:
        if not isinstance(data, list):
            data = [data]

        for record in data:
            table.add_row([record[item] for item in headers])

    click.echo(table)


def sanitize_kwargs(**kwargs):
    kwargs = dict((k, v) for k, v in six.iteritems(kwargs) if v)

    try:
        kwargs['data'] = json.loads(kwargs['data'])
    except KeyError:
        pass

    return kwargs


def format_output(output, format, item=None, headers=None):

    if format == 'json':
        print_json(output)
    else:
        to_display = output[item] if item else output
        print_prettytable(to_display, headers)
