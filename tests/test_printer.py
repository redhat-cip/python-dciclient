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

from dciclient.printer import print_response
from dciclient.v1.shell_commands import user


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
        ]
    )
    result = runner.invoke_raw(["user-list"])
    print_response(
        result, format="table", verbose=True, columns=user.COLUMNS
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
            "pass"
        ]
    )
    result = runner.invoke_raw(["user-list"])
    print_response(
        result, format="table", verbose=False, columns=user.COLUMNS
    )
    captured = capsys.readouterr()
    assert "etag" not in captured.out


def test_printer_delete(capsys, runner, team_id):
    _user = runner.invoke(
        [
            "user-create",
            "--name",
            "todelete",
            "--email",
            "todelete@example.org",
            "--password",
            "pass"
        ]
    )["user"]
    result = runner.invoke_raw(["user-delete", _user["id"], "--etag", _user["etag"]])
    print_response(result, format="table", verbose=False, columns=user.COLUMNS)
    captured = capsys.readouterr()
    assert captured.out == ""
