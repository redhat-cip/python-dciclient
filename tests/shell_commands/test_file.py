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

from __future__ import unicode_literals


def test_show(runner, file_id):
    file = runner.invoke(["file-show", file_id])["file"]
    assert file["id"] == file_id


def test_content(runner, file_id):
    result = runner.invoke_raw(["file-content", file_id])
    assert "testsuite errors" in result.text


def test_list(runner, job_id):
    files = runner.invoke(["file-list", job_id])["files"]
    assert len(files)
    assert "res_junit.xml" in [i["name"] for i in files]


def test_delete(runner, file_id):
    result = runner.invoke_raw(["file-delete", file_id])
    assert result.status_code == 204


def test_where_on_list(runner, job_id):
    files = runner.invoke(["file-list", job_id, "--where", "size:785"])['files']
    assert len(files) == 1
    assert files[0]['size'] == 785


def test_query_on_list(runner, job_id):
    files = runner.invoke(["file-list", job_id, "--query", "eq(size,785)"])['files']
    assert len(files) == 1
    assert files[0]['size'] == 785
