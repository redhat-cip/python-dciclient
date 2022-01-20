import csv
import json

import prettytable

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def _tablify_result(data):
    """Convert the JSON dict structure to a regular list."""
    if isinstance(data, dict):
        keys = [i for i in list(data.keys()) if i != "_meta"]
        if len(keys) == 1:
            data = data[keys[0]]
    if not isinstance(data, list):
        data = [data]
    return data


def _find_headers_from_data(data):
    """Return the header names from the data."""
    if isinstance(data, list):
        first_row = data[0] if len(data) else {}
    else:
        first_row = data
    return list(first_row.keys())


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


def _print_csv(data, headers, skip_columns, delimiter=","):
    f = StringIO()
    data = _tablify_result(data)
    headers = headers or _find_headers_from_data(data)
    headers = _sort_headers(headers)
    headers = [i for i in headers if i not in skip_columns]
    data = [{k: v for k, v in d.items() if k not in skip_columns} for d in data]
    output = csv.DictWriter(f, headers, delimiter=delimiter)
    output.writerows(data)
    print(f.getvalue())


def _print_tsv(data, headers, skip_columns):
    return _print_csv(data, headers, skip_columns, delimiter="\t")


def _print_json(result_json):
    formatted_result = json.dumps(result_json, indent=4)
    print(formatted_result)


def _get_field(record, field_path):
    cur_field = field_path.pop(0)
    v = record.get(cur_field)
    if len(field_path):
        return _get_field(record[cur_field], field_path)
    else:
        return v


def _print_prettytable(data, headers=None, skip_columns=[]):
    data = _tablify_result(data)
    headers = headers or _find_headers_from_data(data)
    headers = _sort_headers(headers)
    headers = [i for i in headers if i not in skip_columns]
    table = prettytable.PrettyTable(headers)

    for record in data:
        row = []
        for item in headers:
            row.append(_get_field(record, field_path=item.split("/")))
        table.add_row(row)

    print(table)


def print_response(response, format, verbose, columns):
    try:
        if response.status_code == 204:
            return
        result_json = response.json()
        skip_columns = [] if verbose else ["etag", "created_at", "updated_at", "data"]
        if format == "csv":
            _print_csv(result_json, columns, skip_columns)
        if format == "tsv":
            _print_tsv(result_json, columns, skip_columns)
        if format == "json":
            _print_json(result_json)
        if format == "table":
            _print_prettytable(result_json, columns, skip_columns)
    except Exception:
        print(response)
