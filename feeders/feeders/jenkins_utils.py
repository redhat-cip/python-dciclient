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
import requests

import re


requests.packages.urllib3.disable_warnings()


def get_builds_from_job(job_url):
    tree = {'tree': 'builds[numer,url,result]'}
    r = requests.get('%s/api/json' % job_url, params=tree, verify=False)
    return json.loads(r.text)['builds']


def get_puddle_ids_from_build(build, puddles):
    puddle_ids = []
    routput = requests.get('%s/consoleText' % build['url'], verify=False)
    m = re.search(r'^# rhos-release 8 *-p *(.*)', routput.text, re.MULTILINE)
    if m:
        # get the components with its name
        for puddle in puddles:
            if m.group(1) == puddle['name']:
                puddle_ids.append(puddle['id'])
    return puddle_ids


def get_job_status(status):
    statuses = {'SUCCESS': 'success', 'UNSTABLE': 'success',
                'FAILURE': 'failure', 'ABORTED': 'failure'}
    return statuses.get(status, 'failure')


def get_nosetests_url(url):
    r = requests.get('%s/api/json' % url, verify=False)
    build = json.loads(r.text)
    for artifact in build['artifacts']:
        if artifact['fileName'] == 'nosetests.xml':
            return artifact['relativePath']


def get_nosetests_content(base_url, rel_url):
    r = requests.get('%s/artifact/%s' % (base_url, rel_url), verify=False)
    content = r.text
    return content


def get_jenkins_jobs(config):
    jenkins = config['jenkins']
    jenkins_jobdefinition = []
    views = jenkins.get('views', [])
    multijobs = jenkins.get('multijobs', [])
    jobs = jenkins.get('jobs', [])
    for unitjob in jobs:
        r = requests.get('%s/api/json' % unitjob, verify=False)
        unitjob = json.loads(r.text)
        jenkins_jobdefinition.append(unitjob)
    for view in views:
        r = requests.get('%s/api/json' % view, verify=False)
        jenkins_jobdefinition.extend(json.loads(r.text)['jobs'])
    for mjob in multijobs:
        r = requests.get('%s/api/json' % mjob, verify=False)
        mjob = json.loads(r.text)
        for jjobdef in mjob['downstreamProjects']:
            jenkins_jobdefinition.append(jjobdef)
    return jenkins_jobdefinition
