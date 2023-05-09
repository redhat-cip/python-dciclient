# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Red Hat, Inc.
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

from argparse import Namespace
from dciclient.v1 import utils


def test_flatten():
    s = {"jim": 123, "a": {"b": {"c": {"d": "bob"}}}, "rob": 34}
    r = utils.flatten(s)
    r.sort()
    assert r == ["a.b.c.d=bob", "jim=123", "rob=34"]


def test_get_search_params():
    assert utils.get_search_params(
        Namespace(
            **{
                "sort": "-created_at",
                "limit": 1,
                "offset": 0,
                "where": "name:OpenShift",
                "query": "",
            }
        )
    ) == {
        "sort": "-created_at",
        "limit": 1,
        "offset": 0,
        "where": "name:OpenShift",
    }
    assert utils.get_search_params(
        Namespace(
            **{
                "sort": "",
                "limit": 100,
                "offset": 0,
                "where": None,
                "query": None,
            }
        )
    ) == {
        "limit": 100,
        "offset": 0,
    }
