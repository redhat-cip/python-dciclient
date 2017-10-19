# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2017 Red Hat, Inc
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

import click
import json
import prettytable


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


def _get_field(record, field_path):
    cur_field = field_path.pop(0)
    v = record.get(cur_field)
    if len(field_path):
        return _get_field(record[cur_field], field_path)
    else:
        return v


def print_prettytable(data, headers=None, skip_columns=[]):
    def sort_headers(headers):
        """Ensure the column order is always the same."""
        headers = set(headers)
        default_order = [
            'id', 'name', 'etag', 'created_at',
            'updated_at', 'state', 'data']
        sorted_headers = []
        for i in default_order:
            if i not in headers:
                continue
            headers.remove(i)
            sorted_headers.append(i)
        sorted_headers += sorted(headers)
        return sorted_headers

    def tablify_result(data):
        """Convert the JSON dict structure to a regular list."""
        if isinstance(data, dict):
            keys = [i for i in list(data.keys()) if i != '_meta']
            if len(keys) == 1:
                data = data[keys[0]]

        if not isinstance(data, list):
            data = [data]
        return data

    def find_headers_from_data(data):
        """Return the header names from the data."""
        if isinstance(data, list):
            first_row = data[0] if len(data) else {}
        else:
            first_row = data
        return list(first_row.keys())

    data = tablify_result(data)
    headers = headers or find_headers_from_data(data)
    headers = sort_headers(headers)
    headers = [i for i in headers if i not in skip_columns]
    table = prettytable.PrettyTable(headers)

    for record in data:
        row = []
        for item in headers:
            row.append(_get_field(record, field_path=item.split('/')))
        table.add_row(row)

    click.echo(table)


def sanitize_kwargs(**kwargs):
    boolean_fields = ['active', 'export_control']

    for k in list(kwargs.keys()):
        if kwargs[k] is None:
            if k in boolean_fields:
                kwargs[k] = bool(kwargs[k])
            else:
                del(kwargs[k])
    try:
        kwargs['data'] = json.loads(kwargs['data'])
    except (KeyError, TypeError):
        pass

    return kwargs


def format_output(result, format, headers=None,
                  success_code=(200, 201, 204),
                  item=None, verbose=True):

    skip_columns = []
    if not verbose:
        skip_columns = ['etag', 'created_at', 'updated_at', 'data']

    is_failure = False
    if hasattr(result, 'json'):
        if result.status_code not in success_code:
            is_failure = True
        result = result.json()

    if format == 'json' or is_failure:
        print_json(result)
    else:
        # if our strucutre come with only one root key,
        # we can assume it's the item type.
        if not item and isinstance(result, dict):
            values = list(result.values())
            if len(values) == 1:
                result = values[0]
        to_display = result[item] if item else result
        if to_display:
            print_prettytable(to_display, headers, skip_columns)


def validate_json(ctx, param, value):
    if value is None:
        return
    try:
        return json.loads(value)
    except ValueError:
        raise click.BadParameter('this option expects a valid JSON')


def active_string(value):
    return {None: None, True: 'active', False: 'inactive'}[value]
