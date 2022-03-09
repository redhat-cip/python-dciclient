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

from dciclient.v1.api import file as dci_file
from dciclient.v1.api import job


def list(context, args):
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "where"]}
    params["embed"] = "topic,remoteci,team"
    return job.list(context, **params)


def show(context, args):
    return job.get(context, id=args.id)


def delete(context, args):
    return job.delete(context, id=args.id, etag=args.etag)


def list_results(context, args):
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "id"]}
    return job.list_results(context, **params)


def output(context, args):
    result = job.list_jobstates(context, id=args.id, sort="created_at")
    jobstates = result.json()["jobstates"]

    res = []
    for js in jobstates:
        f_l = job.list_files(
            context, id=args.id, where="jobstate_id:" + js["id"], sort="created_at"
        )
        for f in f_l.json()["files"]:
            res.append(dci_file.content(context, id=f["id"]).text)
    return res


def list_tests(context, args):
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "id", "where"]}
    return job.list_tests(context, **params)


def file_upload(context, args):
    params = {
        k: getattr(args, k)
        for k in ["job_id", "name", "file_path", "jobstate_id", "mime"]
    }
    return dci_file.create_with_stream(context, **params)


def file_download(context, args):
    params = {k: getattr(args, k) for k in ["id", "file_id", "target"]}
    dci_file.download(context, **params)


def file_show(context, args):
    return dci_file.get(context, id=args.file_id)


def file_list(context, args):
    params = {k: getattr(args, k) for k in ["sort", "limit", "offset", "id", "where"]}
    return job.list_files(context, **params)


def file_delete(context, args):
    dci_file.delete(context, id=args.file_id)
    return dci_file.delete(context, id=args.file_id)
