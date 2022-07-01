# -*- encoding: utf-8 -*-
#
# Copyright 2017-2022 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

RESOURCE = "identity"


def get(context):
    uri = "%s/%s" % (context.dci_cs_api, RESOURCE)
    return context.session.get(uri)


def my_team_id(context):
    """Get team id of the current user.

    If it's a remoteci there is only one team id possible.
    If it's a regular user, it might belongs to multiple teams, this
    function will return one randomly.
    """
    res = get(context)
    res.raise_for_status()
    res = res.json()
    return next(iter(res["identity"]["teams"].keys()))
