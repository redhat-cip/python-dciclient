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

import yaml
import json
import requests
import re

from dciclient.v1.api import component
from dciclient.v1.api import context as dcicontext
from dciclient.v1.api import jobdefinition as dcijobdef
from dciclient.v1.api import job as dcijob
from dciclient.v1.api import jobstate as dcijobstate

requests.packages.urllib3.disable_warnings()

def get_puddles(config, cache=None):
    r = requests.get(config["puddle"]["url"])
    m = re.findall(r"href=.*>([0-9]{4}-[0-9]{2}-[0-9]{2}\.[0-9]+)/</a>", r.text, re.MULTILINE)
    return m

def add_puddle_as_component(config, dci_context, puddles):
    dci_puddles = json.loads(component.list(dci_context, topic_id).text)
    clean_puddles = []
    for puddle in puddles:
        result = json.loads(component.create(dci_context, puddle, component.PUDDLE ,config['dci']['topic_id']).text)
        if 'status_code' in result.keys() and result['status_code'] == 422:
            result = [x for x in dci_puddles['components'] if x['name'] == puddle]
            clean_puddles.append(result[0])
        else:
            clean_puddles.append(result)
    return clean_puddles

def get_jenkins_jobs(dcicontext, topic_id, puddles, config, cache=None):
    job_array = []
    # view page to grab job page
    views = [config['jenkins']['views']]
    # Multijob page to grab downstream jobs
    multijobs = [config['jenkins']['multijobs']]
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
    jobdef_in_dci=json.loads(dcijobdef.list(dcicontext, topic_id, embed='jobdefinition_component').text)
    dci_puddles = json.loads(component.list(dci_context, topic_id, where="type:puddle").text)
    for puddle in puddles:
        for job in job_array:
            flag = 0
            for dcijob in jobdef_in_dci['jobdefinitions']:
                if dcijob['name'] == job['name']:
                    compos = json.loads(dcijobdef.get_components(dcicontext, dcijob['id']).text)
                    for compo in compos['components']:
                        if compo['type'] == "puddle":
                            if compo['name'] == puddle["name"]:
                                flag = 1
                                break
            if flag == 0:
                newjob=json.loads(dcijobdef.create(dcicontext, job['name'], topic_id, test_id=config['dci']['test_id']).text)
                dcijobdef.add_component(dcicontext, newjob['jobdefinition']['id'], puddle["id"])

    temparray = []
    tree = { 'tree' : 'builds[numer,url,result]' }
    for job in job_array:
        r = requests.get("%s/api/json" % job['url'], params=tree, verify=False)
        builds = json.loads(r.text)
        for build in builds['builds']:
            routput = requests.get("%s/consoleText" % build['url'], verify=False)
            m = re.search(r"^# rhos-release 8 *-p *(.*)", routput.text, re.MULTILINE)
            if m:
		temparray.append({ 'name' : job['name'], 'puddle': m.group(1), 'result': build['result'], 'url': build['url']})
    for status in temparray:
	for item in dci_puddles['components']:
            if item['name'] == status['puddle']:
                puddleid = item['id']
                break
	for item in jobdef_in_dci['jobdefinitions']:
            if item['name'] == status['name']:
		if item['jobdefinition_component']['component_id'] == puddleid:
                    jobid = item['id']
        job = json.loads(dcijob.create(dcicontext, False, config['dci']['remoteci_id'], config['dci']['team_id'], jobid).text)
        if status['result'] == "SUCCESS":
            dci_status = "success"
        if status['result'] == "UNSTABLE":
            dci_status = "success"
        if status['result'] == "FAILURE":
            dci_status = "failure"
	if status['result'] == "ABORTED":
            dci_status = "failure"
        
	dcijobstate.create(dcicontext, dci_status, status['url'], job['job']['id'])
         

if __name__ == '__main__':
    config_file = open("config.yaml", "r")
    config = yaml.load(config_file)
    config_file.close()

    topic_id = config['dci']['topic_id']

    dci_context = dcicontext.build_dci_context(
        config['dci']['control_server_url'],
        config['dci']['login'],
        config['dci']['password'])

    puddles = get_puddles(config)
    puddles = add_puddle_as_component(config, dci_context, puddles)
    get_jenkins_jobs(dci_context, topic_id, puddles, config)

