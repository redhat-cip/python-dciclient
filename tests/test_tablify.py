# -*- encoding: utf-8 -*-
#
# Copyright 2015-2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from dciclient.v1.tablify import get_headers_and_sizes_from_data
from dciclient.v1.tablify import format_line
from dciclient.v1.tablify import adjust_column_width_to_console
from dciclient.v1.tablify import adjust_text
from dciclient.v1.tablify import split_strings
from dciclient.v1.tablify import create_line_content
from dciclient.v1.tablify import format_data_line
from dciclient.v1.tablify import format_text
from dciclient.v1.tablify import format_headers_line
from dciclient.v1.utils import format_lines_adjusted_to_console

try:
    from unittest import mock
except ImportError:
    import mock


def test_get_headers_and_sizes_from_data():
    data = [
        {
            "id": "6018975a-dde7-4666-9436-b171c5a11dde",
            "name": "Jonh Doe",
            "email": "jdoe@example.org",
        },
        {
            "id": "f05b3da7-701b-40bd-87e8-780693a07b13",
            "name": "Bob Dylan",
            "email": "bdylan@example.org",
        },
    ]
    options = {"console_width": 32, "headers": ["id", "name", "email"]}

    expected_headers = [
        {"size": 16, "name": "id"},
        {"size": 4, "name": "name"},
        {"size": 8, "name": "email"},
    ]
    assert (
        get_headers_and_sizes_from_data(
            data, options["headers"], options["console_width"]
        )
        == expected_headers
    )


def test_format_line():
    headers_and_sizes = [
        {"size": 5, "name": "id"},
        {"size": 5, "name": "name"},
        {"size": 5, "name": "email"},
    ]

    assert format_line(headers_and_sizes, "top") == u"┌─────┬─────┬─────┐"

    headers_and_sizes = [
        {"size": 5, "name": "id"},
        {"size": 10, "name": "name"},
        {"size": 5, "name": "email"},
    ]
    assert format_line(headers_and_sizes, "separator") == u"├─────┼──────────┼─────┤"

    headers_and_sizes = [
        {"size": 5, "name": "id"},
        {"size": 10, "name": "name"},
        {"size": 5, "name": "email"},
    ]
    assert format_line(headers_and_sizes, "bottom") == u"└─────┴──────────┴─────┘"


def test_adjust_column_width_to_console():
    data = [
        {"size": 36, "name": "id"},
        {"size": 9, "name": "name"},
        {"size": 18, "name": "email"},
    ]
    expected_headers = [
        {"size": 16, "name": "id"},
        {"size": 4, "name": "name"},
        {"size": 8, "name": "email"},
    ]
    assert adjust_column_width_to_console(data, console_width=32) == expected_headers

    data = [
        {"size": 36, "name": "id"},
        {"size": 9, "name": "name"},
        {"size": 18, "name": "email"},
    ]
    expected_headers = [
        {"size": 24, "name": "id"},
        {"size": 6, "name": "name"},
        {"size": 12, "name": "email"},
    ]
    assert adjust_column_width_to_console(data, console_width=46) == expected_headers


def test_adjust_text():
    string = "Jonh Doe"
    assert adjust_text(string, column_width=5) == "Jon\nh D\noe"

    string = "6018975a-dde7-4666-9436-b171c5a11dde"
    assert (
        adjust_text(string, column_width=9)
        == "6018975\na-dde7-\n4666-94\n36-b171\nc5a11dd\ne"
    )


def test_split_strings():
    data = [
        "6018975a-dde7-46\n66-9436-b171c5a1\n1dde",
        "Jo\nnh\nDo\ne",
        "jdoe@ex\nample.o\nrg",
    ]

    expected = [
        ["6018975a-dde7-46", "66-9436-b171c5a1", "1dde"],
        ["Jo", "nh", "Do", "e"],
        ["jdoe@ex", "ample.o", "rg"],
    ]

    assert split_strings(data) == expected


def test_create_line_content():
    data = [
        ["6018975a-dde7-46", "66-9436-b171c5a1", "1dde"],
        ["Jo", "nh", "Do", "e"],
        ["jdoe@ex", "ample.o", "rg"],
    ]

    expected = [
        ["6018975a-dde7-46", "Jo", "jdoe@ex"],
        ["66-9436-b171c5a1", "nh", "ample.o"],
        ["1dde", "Do", "rg"],
        [" ", "e", " "],
    ]

    assert create_line_content(data) == expected


def test_format_data_line():
    data = [
        {
            "id": "6018975a-dde7-4666-9436-b171c5a11dde",
            "name": "Jonh Doe",
            "email": "jdoe@example.org",
        },
    ]
    options = {"console_width": 32, "headers": ["id", "name", "email"]}
    headers = get_headers_and_sizes_from_data(
        data, options["headers"], options["console_width"]
    )
    assert format_data_line(data[0], headers) == [
        u"│ 6018975a-dde7-4 │ Jo │ jdoe@ │",
        u"│ 666-9436-b171c5 │ nh │ examp │",
        u"│ a11dde          │ Do │ le.or │",
        u"│                 │ e  │ g     │",
    ]


def test_format_text():
    headers = [
        {"size": 18, "name": "id"},
        {"size": 4, "name": "name"},
        {"size": 9, "name": "email"},
    ]
    substrings = [["id"], ["na", "me"], ["email"]]
    assert format_text(headers, substrings) == [
        u"│ id               │ na │ email   │",
        u"│                  │ me │         │",
    ]

    headers = [
        {"size": 18, "name": "id"},
        {"size": 4, "name": "name"},
        {"size": 9, "name": "email"},
    ]
    substrings = [
        ["6018975a-dde7-46", "66-9436-b171c5a1", "1dde"],
        ["Jo", "nh", "Do", "e"],
        ["jdoe@ex", "ample.o", "rg"],
    ]
    assert format_text(headers, substrings) == [
        u"│ 6018975a-dde7-46 │ Jo │ jdoe@ex │",
        u"│ 66-9436-b171c5a1 │ nh │ ample.o │",
        u"│ 1dde             │ Do │ rg      │",
        u"│                  │ e  │         │",
    ]


def test_format_headers_line():
    headers = [
        {"size": 18, "name": "id"},
        {"size": 4, "name": "name"},
        {"size": 9, "name": "email"},
    ]
    expected = [
        u"│ id               │ na │ email   │",
        u"│                  │ me │         │",
    ]

    assert format_headers_line(headers) == expected


def test_format_lines_adjusted_to_console():
    data = [
        {
            "id": "6018975a-dde7-4666-9436-b171c5a11dde",
            "name": "Jonh Doe",
            "email": "jdoe@example.org",
        },
    ]
    options = {"console_width": 32}
    expected = [
        u"┌─────────────────┬────┬───────┐",
        u"│ id              │ na │ email │",
        u"│                 │ me │       │",
        u"├─────────────────┼────┼───────┤",
        u"│ 6018975a-dde7-4 │ Jo │ jdoe@ │",
        u"│ 666-9436-b171c5 │ nh │ examp │",
        u"│ a11dde          │ Do │ le.or │",
        u"│                 │ e  │ g     │",
        u"└─────────────────┴────┴───────┘",
    ]
    assert format_lines_adjusted_to_console(data, options) == expected

    data = [
        {
            "id": "6018975a-dde7-4666-9436-b171c5a11dde",
            "name": "Jonh Doe",
            "email": "jdoe@example.org",
        },
        {
            "id": "f05b3da7-701b-40bd-87e8-780693a07b13",
            "name": "Bob Dylan",
            "email": "bdylan@example.org",
        },
    ]
    options = {"console_width": 32, "skip_columns": ["id"]}
    expected = [
        u"┌──────────┬───────────────────┐",
        u"│ name     │ email             │",
        u"├──────────┼───────────────────┤",
        u"│ Jonh Doe │ jdoe@example.org  │",
        u"├──────────┼───────────────────┤",
        u"│ Bob Dyla │ bdylan@example.or │",
        u"│ n        │ g                 │",
        u"└──────────┴───────────────────┘",
    ]
    assert format_lines_adjusted_to_console(data, options) == expected

    data = [
        {
            "id": "6018975a-dde7-4666-9436-b171c5a11dde",
            "name": "Jonh Doe",
            "email": "jdoe@example.org",
        },
    ]
    options = {"console_width": 32, "skip_columns": ["name", "email"]}
    expected = [
        u"┌──────────────────────────────┐",
        u"│ id                           │",
        u"├──────────────────────────────┤",
        u"│ 6018975a-dde7-4666-9436-b171 │",
        u"│ c5a11dde                     │",
        u"└──────────────────────────────┘",
    ]
    assert format_lines_adjusted_to_console(data, options) == expected

    # DEFAULT  CONSOLE WIDTH
    with mock.patch("dciclient.printer.get_default_console_width") as post_mock:
        post_mock.return_value = 207
        data = [
            {
                "id": "6018975a-dde7-4666-9436-b171c5a11dde",
                "name": "Jonh Doe",
                "email": "jdoe@example.org",
            },
        ]
        expected = [
            u"┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬───────────────────────────┬──────────────────────────────────────────────────────┐",  # noqa
            u"│ id                                                                                                                       │ name                      │ email                                                │",  # noqa
            u"├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────┼──────────────────────────────────────────────────────┤",  # noqa
            u"│ 6018975a-dde7-4666-9436-b171c5a11dde                                                                                     │ Jonh Doe                  │ jdoe@example.org                                     │",  # noqa
            u"└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴───────────────────────────┴──────────────────────────────────────────────────────┘",  # noqa
        ]
        assert format_lines_adjusted_to_console(data) == expected

    # DEFAULT HEADERS
    data = [
        {
            "id": "6018975a-dde7-4666-9436-b171c5a11dde",
            "name": "Jonh Doe",
            "email": "jdoe@example.org",
        },
    ]
    options = {"console_width": 32}
    expected = [
        u"┌─────────────────┬────┬───────┐",
        u"│ id              │ na │ email │",
        u"│                 │ me │       │",
        u"├─────────────────┼────┼───────┤",
        u"│ 6018975a-dde7-4 │ Jo │ jdoe@ │",
        u"│ 666-9436-b171c5 │ nh │ examp │",
        u"│ a11dde          │ Do │ le.or │",
        u"│                 │ e  │ g     │",
        u"└─────────────────┴────┴───────┘",
    ]
    assert format_lines_adjusted_to_console(data, options) == expected

    # DEFAULT CONSOLE WIDTH, 1 COLUMN
    with mock.patch("dciclient.printer.get_default_console_width") as post_mock:
        post_mock.return_value = 207
        data = [
            {
                "id": "6018975a-dde7-4666-9436-b171c5a11dde",
                "name": "Jonh Doe",
                "email": "jdoe@example.org",
            },
        ]
        options = {"skip_columns": ["name", "email"]}
        expected = [
            u"┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐",  # noqa
            u"│ id                                                                                                                                                                                                          │",  # noqa
            u"├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤",  # noqa
            u"│ 6018975a-dde7-4666-9436-b171c5a11dde                                                                                                                                                                        │",  # noqa
            u"└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘",  # noqa
        ]
        assert format_lines_adjusted_to_console(data, options) == expected

    # DIFFERENT DATA FORMATS
    with mock.patch("dciclient.printer.get_default_console_width") as post_mock:
        post_mock.return_value = 207
        data = [
            {"id": True, "name": "Jonh Doe", "email": 42},
        ]
        expected = [
            u"┌────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────┐",  # noqa
            u"│ id                                             │ name                                                                                           │ email                                                     │",  # noqa
            u"├────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────┤",  # noqa
            u"│ True                                           │ Jonh Doe                                                                                       │ 42                                                        │",  # noqa
            u"└────────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────┘",  # noqa
        ]
        assert format_lines_adjusted_to_console(data) == expected

    # EMPTY DATA, NO OPTIONS
    data = []
    assert format_lines_adjusted_to_console(data) == []


def test_printer(capsys, runner, team_id):
    runner.invoke_raw(
        [
            "user-create",
            "--name",
            "foo",
            "--email",
            "foo@example.org",
            "--password",
            "pass",
            "--team-id",
            team_id,
        ]
    )
    print_response(
        runner.invoke_raw(["user-list"]), format="table", verbose=True,
    )
    captured = capsys.readouterr()
    assert "etag" in captured.out


def test_printer_verbose(capsys, runner, team_id):
    runner.invoke_raw(
        [
            "user-create",
            "--name",
            "foo",
            "--email",
            "foo@example.org",
            "--password",
            "pass",
            "--team-id",
            team_id,
        ]
    )
    print_response(
        runner.invoke_raw(["user-list"]), format="table", verbose=False,
    )
    captured = capsys.readouterr()
    assert "etag" not in captured.out


def test_printer_delete(capsys, runner, team_id):
    user = runner.invoke(
        [
            "user-create",
            "--name",
            "todelete",
            "--email",
            "todelete@example.org",
            "--password",
            "pass",
            "--team-id",
            team_id,
        ]
    )["user"]
    result = runner.invoke_raw(["user-delete", user["id"], "--etag", user["etag"]])
    print_response(result, format="table", verbose=False)
    captured = capsys.readouterr()
    assert captured.out == ""
