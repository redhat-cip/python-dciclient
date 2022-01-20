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

import json
from dciclient.v1.exceptions import BadParameter


def flatten(d, prefix=""):
    ret = []
    for k, v in d.items():
        p = k if not prefix else prefix + "." + k
        if isinstance(v, dict):
            ret += flatten(v, prefix=p)
        else:
            ret.append("%s=%s" % (p, v))
    return ret


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


def validate_json(ctx, param, value):
    if value is None:
        return
    try:
        return json.loads(value)
    except ValueError:
        raise BadParameter("this option expects a valid JSON")


def active_string(value):
    return {None: None, True: "active", False: "inactive"}[value]
