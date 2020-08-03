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

import csv
import json
from dciclient.v1.exceptions import BadParameter

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


from dciclient.printer import (
    get_headers_and_sizes_from_data,
    format_line,
    format_data_line,
    format_headers_line,
    _data_to_string,
    get_default_console_width,
    printer,
)


def flatten(d, prefix=""):
    ret = []
    for k, v in d.items():
        p = k if not prefix else prefix + "." + k
        if isinstance(v, dict):
            ret += flatten(v, prefix=p)
        else:
            ret.append("%s=%s" % (p, v))
    return ret


def print_json(result_json):
    formatted_result = json.dumps(result_json, indent=4)
    print(formatted_result)


def print_csv(data, headers, skip_columns, delimiter=","):
    f = StringIO()
    data = _tablify_result(data)
    headers = headers or _find_headers_from_data(data)
    headers = _sort_headers(headers)
    headers = [i for i in headers if i not in skip_columns]
    data = [{k: v for k, v in d.items() if k not in skip_columns} for d in data]
    output = csv.DictWriter(f, headers, delimiter=delimiter)
    output.writerows(data)
    print(f.getvalue())


def _get_field(record, field_path):
    cur_field = field_path.pop(0)
    v = record.get(cur_field)
    if len(field_path):
        return _get_field(record[cur_field], field_path)
    else:
        return v


def _find_headers_from_data(data):
    """Return the header names from the data."""
    if isinstance(data, list):
        first_row = data[0] if len(data) else {}
    else:
        first_row = data
    return list(first_row.keys())


def _tablify_result(data):
    """Convert the JSON dict structure to a regular list."""
    if isinstance(data, dict):
        keys = [i for i in list(data.keys()) if i != "_meta"]
        if len(keys) == 1:
            data = data[keys[0]]
    if not isinstance(data, list):
        data = [data]
    return data


def _sort_headers(headers):
    """Ensure the column order is always the same."""
    headers = set(headers)
    default_order = ["id", "name", "etag", "created_at", "updated_at", "state", "data"]
    sorted_headers = []
    for i in default_order:
        if i not in headers:
            continue
        headers.remove(i)
        sorted_headers.append(i)
    sorted_headers += sorted(headers)
    return sorted_headers


def format_lines_adjusted_to_console(data, options={}, sort_callback=_sort_headers):
    if not data:
        return []

    data = _tablify_result(data)

    headers = _find_headers_from_data(data)
    headers = _sort_headers(headers)

    if "skip_columns" in options:
        headers = [i for i in headers if i not in options["skip_columns"]]

    console_width = (
        options["console_width"]
        if "console_width" in options
        else get_default_console_width()
    )

    data = _data_to_string(data)

    headers_and_sizes = get_headers_and_sizes_from_data(data, headers, console_width)
    if headers_and_sizes == '[]':
        json_object = json.dumps(data, indent=4)
        print(json_object)
        exit(1)

    lines_to_print = []
    lines_to_print.append(format_line(headers_and_sizes, "top"))

    headers_line = format_headers_line(headers_and_sizes)
    for string in headers_line:
        lines_to_print.append(string)
    lines_to_print.append(format_line(headers_and_sizes, "separator"))

    for row in data[:-1]:
        data_line = format_data_line(row, headers_and_sizes)
        for string in data_line:
            lines_to_print.append(string)
        lines_to_print.append(format_line(headers_and_sizes, "separator"))

    data_last_row = format_data_line(data[-1], headers_and_sizes)
    for string in data_last_row:
        lines_to_print.append(string)
    lines_to_print.append(format_line(headers_and_sizes, "bottom"))

    return lines_to_print


def sanitize_kwargs(**kwargs):
    boolean_fields = ["active"]

    for k in list(kwargs.keys()):
        if kwargs[k] is None:
            if k in boolean_fields:
                kwargs[k] = bool(kwargs[k])
            else:
                del kwargs[k]
    try:
        kwargs["data"] = json.loads(kwargs["data"])
    except (KeyError, TypeError):
        pass

    return kwargs


def format_output(
    result, format, headers=None, success_code=(200, 201, 204), item=None, verbose=True
):

    skip_columns = []
    if not verbose:
        skip_columns = ["etag", "created_at", "updated_at", "data"]

    is_failure = False
    if hasattr(result, "json"):
        if result.status_code not in success_code:
            is_failure = True
        result = result.json()

    if format == "json" or is_failure:
        print_json(result)
        return

    # if our structure come with only one root key,
    # we can assume it's the item type.
    if not item and isinstance(result, dict):
        values = list(result.values())
        if len(values) == 1:
            result = values[0]
    to_display = result[item] if item else result
    if to_display:
        if format in ["csv", "tsv"]:
            delimiter = "\t" if format == "tsv" else ","
            print_csv(to_display, headers, skip_columns, delimiter=delimiter)
        else:
            lines_to_print = format_lines_adjusted_to_console(
                to_display,
                options={
                    "skip_columns": skip_columns,
                },
            )
            printer(lines_to_print)


def validate_json(ctx, param, value):
    if value is None:
        return
    try:
        return json.loads(value)
    except ValueError:
        raise BadParameter("this option expects a valid JSON")


def active_string(value):
    return {None: None, True: "active", False: "inactive"}[value]
