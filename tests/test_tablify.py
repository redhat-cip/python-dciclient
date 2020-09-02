# -*- encoding: utf-8 -*-
#
# Copyright 2020 Red Hat, Inc.
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

from dciclient.v1.tablify import format_lines_adjusted_to_console


def test_format_lines_with_ajusted_console():
    data = [
        {
            "id": "6018975a-dde7-4666-9436-b171c5a11dde",
            "name": "Jonh Doe",
            "email": "jdoe@example.org",
        },
    ]
    options = {"console_width": 32, "headers": ["id", "name", "email"]}
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


def test_format_lines_with_ajusted_console_and_skipped_column():
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
    options = {"console_width": 32, "headers": ["name", "email"]}
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


def test_format_lines_with_ajusted_console_with_one_column():
    data = [
        {
            "id": "6018975a-dde7-4666-9436-b171c5a11dde",
            "name": "Jonh Doe",
            "email": "jdoe@example.org",
        },
    ]
    options = {"console_width": 32, "headers": ["id"]}
    expected = [
        u"┌──────────────────────────────┐",
        u"│ id                           │",
        u"├──────────────────────────────┤",
        u"│ 6018975a-dde7-4666-9436-b171 │",
        u"│ c5a11dde                     │",
        u"└──────────────────────────────┘",
    ]
    assert format_lines_adjusted_to_console(data, options) == expected


def test_format_lines_with_big_screen():
    data = [
        {
            "id": "6018975a-dde7-4666-9436-b171c5a11dde",
            "name": "Jonh Doe",
            "email": "jdoe@example.org",
        },
    ]
    options = {"console_width": 207, "headers": ["id", "name", "email"]}
    expected = [
        u"┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬───────────────────────────┬──────────────────────────────────────────────────────┐",  # noqa
        u"│ id                                                                                                                       │ name                      │ email                                                │",  # noqa
        u"├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────┼──────────────────────────────────────────────────────┤",  # noqa
        u"│ 6018975a-dde7-4666-9436-b171c5a11dde                                                                                     │ Jonh Doe                  │ jdoe@example.org                                     │",  # noqa
        u"└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴───────────────────────────┴──────────────────────────────────────────────────────┘",  # noqa
    ]
    assert format_lines_adjusted_to_console(data, options) == expected


def test_format_lines_with_boolean():
    data = [
        {"id": True, "name": "Jonh Doe", "email": 42},
    ]
    options = {"console_width": 207, "headers": ["id", "name", "email"]}
    expected = [
        u"┌────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────┐",  # noqa
        u"│ id                                             │ name                                                                                           │ email                                                     │",  # noqa
        u"├────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────┤",  # noqa
        u"│ True                                           │ Jonh Doe                                                                                       │ 42                                                        │",  # noqa
        u"└────────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────┘",  # noqa
    ]
    assert format_lines_adjusted_to_console(data, options) == expected


def test_format_lines_without_any_data():
    data = []
    assert format_lines_adjusted_to_console(data, {"console_width": 80}) == []
