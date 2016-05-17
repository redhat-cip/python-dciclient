#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2016 Red Hat, Inc.
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

import json
import re
import requests
import yaml

from dciclient.v1.api import component
from dciclient.v1.api import context as dcicontext
from dciclient.v1.api import file as dcifile
from dciclient.v1.api import job as dcijob
from dciclient.v1.api import jobdefinition as dcijobdef
from dciclient.v1.api import jobstate as dcijobstate
from tqdm import tqdm

requests.packages.urllib3.disable_warnings()


def get_puddles(config, cache=None):
    print("Grabbing Puddles from %s" % config["puddle"]["url"])
    r = requests.get(config["puddle"]["url"])
    m = re.findall(r"href=.*>([0-9]{4}-[0-9]{2}-[0-9]{2}\.[0-9]+)/</a>",
                   r.text, re.MULTILINE)
    return m


def add_puddle_as_component(config, dci_context, puddles):
    dci_puddles = json.loads(component.list(dci_context, topic_id).text)
    clean_puddles = []
    print("Adding puddles")
    for puddle in tqdm(puddles):
        result = json.loads(component.create(dci_context,
                                             puddle,
                                             component.PUDDLE,
                                             config['dci']['topic_id']).text)
        if 'status_code' in result.keys() and result['status_code'] == 422:
            result = [x for x in dci_puddles['components']
                      if x['name'] == puddle]
            clean_puddles.append(result[0])
        else:
            clean_puddles.append(result)
    return clean_puddles


def get_builds_from_job(job_url):
    tree = {'tree': 'builds[numer,url,result]'}
    r = requests.get("%s/api/json" % job_url, params=tree, verify=False)
    builds = json.loads(r.text)
    return builds['builds']


def get_puddlev_from_build(build, puddles):
    routput = requests.get("%s/consoleText" % build['url'], verify=False)
    m = re.search(r"^# rhos-release 8 *-p *(.*)", routput.text, re.MULTILINE)
    if m:
        for puddle in puddles:
            if m.group(1) == puddle["name"]:
                return puddle["id"]
    return None


def get_job_status(status):
    if status == "SUCCESS":
        return "success"
    if status == "UNSTABLE":
        return "success"
    if status == "FAILURE":
        return "failure"
    if status == "ABORTED":
        return "failure"
    return "failure"


def get_nosetests_url(url):
    r = requests.get("%s/api/json" % url, verify=False)
    build = json.loads(r.text)
    for artifact in build["artifacts"]:
        if artifact["fileName"] == "nosetests.xml":
            return artifact["relativePath"]
    return None


def get_nosetests_content(base_url, rel_url):
    r = requests.get("%s/artifact/%s" % (base_url, rel_url), verify=False)
    content = r.text
    return content


def get_jenkins_jobs(dcicontext, topic_id, puddles, remoteci_id,
                     team_id, test_id, cache=None):
    job_array = []
    views = []
    multijobs = []
    jobs = []
    # view page to grab job page
    if 'views' in config['jenkins']:
        views = config['jenkins']['views']
    # Multijob page to grab downstream jobs
    if 'multijobs' in config['jenkins']:
        multijobs = config['jenkins']['multijobs']
    if 'jobs' in config['jenkins']:
        jobs = config['jenkins']['jobs']
    for unitjob in jobs:
        r = requests.get("%s/api/json" % unitjob, verify=False)
        unitjob = json.loads(r.text)
        job_array.append(unitjob)
    for view in views:
        r = requests.get("%s/api/json" % view, verify=False)
        view = json.loads(r.text)
        for job in view['jobs']:
            job_array.append(job)
    for mjob in multijobs:
        r = requests.get("%s/api/json" % mjob, verify=False)
        mjob = json.loads(r.text)
        for job in mjob['downstreamProjects']:
            job_array.append(job)

    jobdef_in_dci = json.loads(dcijobdef.list(
        dcicontext,
        topic_id,
        embed='jobdefinition_component').text)

    print('Grabbed %s job definition in DCI'
          % len(jobdef_in_dci['jobdefinitions']))

    dci_puddles = json.loads(component.list(
        dci_context,
        topic_id,
        where="type:puddle").text)

    print('Grabbed %s puddles in DCI' % len(dci_puddles['components']))
    print('Grabbed %s jobs in Jenkins' % len(job_array))

    joblist = json.loads(dcijob.list(dci_context).text)

    # Find all job to be created in DCI
    print('Processing %s potential new job definitions in DCI'
          % (len(puddles) * len(job_array)))

    with tqdm(total=len(puddles) * len(job_array)) as pbar:
        for puddle in puddles:
            for job in job_array:
                pbar.update(1)
                flag = 0
                for dci_job in jobdef_in_dci['jobdefinitions']:
                    cid = dci_job['jobdefinition_component']['component_id']
                    if dci_job['name'] == job['name']:
                        if cid == puddle["id"]:
                            flag = 1
                            break
                if flag == 0:
                    newjob = json.loads(dcijobdef.create(
                        dcicontext,
                        job['name'],
                        topic_id).text)
                    dcijobdef.add_component(
                        dcicontext,
                        newjob['jobdefinition']['id'],
                        puddle["id"])

    # Parsing all logs to find puddles / status per build
    temparray = []
    for job in job_array:
        print("Searching %s" % job['name'])
        builds = get_builds_from_job(job['url'])
        print("- %s Builds found" % len(builds))
        for build in tqdm(builds):
            flag = 0
            for i in joblist["jobs"]:
                if i["comment"] == build["url"]:
                    flag = 1
                    break
            if flag:
                continue
            puddlev = get_puddlev_from_build(build, dci_puddles['components'])
            if puddlev:
                temparray.append(
                    {'name': job['name'],
                     'puddle': puddlev,
                     'result': build['result'],
                     'url': build['url']})
        print("- %s Build with puddles found" % len(temparray))
    print("Adding status found in DCI")

    # Update DCI jobdef list
    jobdef_in_dci = json.loads(
        dcijobdef.list(
            dcicontext,
            topic_id,
            embed='jobdefinition_component').text)

    # Parse all status to put the right jenkins
    # status in the right DCI jobstate
    for status in tqdm(temparray):
        for item in jobdef_in_dci['jobdefinitions']:
            if item['name'] == status['name']:
                cid = item['jobdefinition_component']['component_id']
                if cid == status["puddle"]:
                    jobid = item['id']
        flag = 0
        for jobit in joblist["jobs"]:
            if jobit["comment"] == status["url"]:
                flag = 1
                break

        if flag == 0:
            job = json.loads(
                dcijob.create(
                    dcicontext,
                    False,
                    remoteci_id,
                    team_id,
                    jobid,
                    status["url"]).text)
            state = json.loads(
                dcijobstate.create(
                    dcicontext,
                    get_job_status(status['result']),
                    status['url'],
                    job['job']['id']).text)

            nose_url = get_nosetests_url(status["url"])
            if nose_url:
                dcifile.create(
                    dcicontext,
                    "nosetests.xml",
                    get_nosetests_content(status["url"], nose_url),
                    "application/junit",
                    state["jobstate"]["id"],
                    job_id=job['job']['id'])


if __name__ == '__main__':
    config_file = open("config.yaml", "r")
    config = yaml.load(config_file)
    config_file.close()

    topic_id = config['dci']['topic_id']
    test_id = config['dci']['test_id']
    remoteci_id = config['dci']['remoteci_id']
    team_id = config['dci']['team_id']

    dci_context = dcicontext.build_dci_context(
        config['dci']['control_server_url'],
        config['dci']['login'],
        config['dci']['password']
    )

    puddles = get_puddles(config)
    puddles = add_puddle_as_component(config, dci_context, puddles)
    get_jenkins_jobs(dci_context, topic_id, puddles,
                     remoteci_id, team_id, test_id)
