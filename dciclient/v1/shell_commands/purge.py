# -*- encoding: utf-8 -*-
#
# Copyright 2015-2017 Red Hat, Inc.
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

from dciclient.v1.api import base


def purge(context, args):
    resources = [
        "components",
        "topics",
        "teams",
        "feeders",
        "remotecis",
        "jobs",
        "files",
        "users",
        "products",
    ]

    l_resources = resources if args.resource is None else args.resource.split(",")

    wrong_resources = [res for res in l_resources if res not in resources]
    test_auth = base.purge(context, "users", **{"force": False})

    if len(wrong_resources) > 0:
        msg = "Unknown resource have been specified: %s" % wrong_resources
        return msg

    elif test_auth.status_code == 401:
        return test_auth

    else:
        purged = {}
        if args.force:
            # If in force mode. First we retrieve the number of items to be
            # purged and then we purge them. This allows to presents meaningful
            # informations to the user that used this command.

            for res in l_resources:
                item_purged = base.purge(context, res, **{"force": False}).json()[
                    "_meta"
                ]["count"]
                if (
                    item_purged
                    and base.purge(context, res, **{"force": True}).status_code == 204
                ):
                    purged[res] = "%s item(s) purged" % item_purged
            return purged
        else:
            # If not in force mode. The various endpoints are queried for the
            # informations about the resources to be purged and displayed.
            for res in l_resources:
                resource_to_delete = base.purge(context, res, **{"force": args.force})
                if resource_to_delete.json()["_meta"]["count"] > 0:
                    purged[res] = resource_to_delete.json()
            return purged
