# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Red Hat, Inc
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


def _get_field(record, field_path):
    cur_field = field_path.pop(0)
    v = record.get(cur_field)
    if len(field_path):
        return _get_field(record[cur_field], field_path)
    else:
        return v


def print_prettytable(data, headers=None):
    def sort_headers(headers):
        """Ensure the column order is always the same."""
        headers = set(headers)
        sorted_headers = []
        for i in ['id', 'name', 'etag', 'created_at', 'updated_ata']:
            if i not in headers:
                continue
            headers.remove(i)
            sorted_headers.append(i)
        sorted_headers += sorted(headers)
        return sorted_headers

    if isinstance(data, dict):
        keys = [i for i in list(data.keys()) if i != '_meta']
        if len(keys) == 1:
            data = data[keys[0]]

    if not headers:
        if isinstance(data, list):
            first_row = data[0] if len(data) else {}
        else:
            first_row = data
        headers = list(first_row.keys())

    headers = sort_headers(headers)
    table = prettytable.PrettyTable(headers)

    if not isinstance(data, list):
        data = [data]

    for record in data:
        row = []
        for item in headers:
            row.append(_get_field(record, field_path=item.split('/')))
        table.add_row(row)

    click.echo(table)


def sanitize_kwargs(**kwargs):
    boolean_fields = ['active', 'export_control']
    kwargs = dict(
        (k, v) for k, v in six.iteritems(kwargs)
        if (k in boolean_fields and v is not None) or v
    )

    try:
        kwargs['data'] = json.loads(kwargs['data'])
    except KeyError:
        pass
    except TypeError:
        pass

    return kwargs


def format_output(result, format, headers=None,
                  success_code=(200, 201, 204), item=None):

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
        print_prettytable(to_display, headers)


def validate_json(ctx, param, value):
    if value is None:
        return
    try:
        return json.loads(value)
    except ValueError:
        raise click.BadParameter('this option expects a valid JSON')
