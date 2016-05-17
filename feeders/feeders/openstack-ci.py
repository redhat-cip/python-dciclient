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

import itertools
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
import jenkins_utils
from tqdm import tqdm

requests.packages.urllib3.disable_warnings()


def get_puddles_from_webserver(puddle_url):
    """Get all the puddle's names from the puddle url."""
    print('[*] Grabbing puddles from %s' % puddle_url)
    resp = requests.get(puddle_url)
    return re.findall(r'href=.*>([0-9]{4}-[0-9]{2}-[0-9]{2}\.[0-9]+)/</a>',
                      resp.text, re.MULTILINE)


def inject_puddles_in_dci_cs(config, dci_context, puddles):
    """Adds the new puddles in the DCI CS if they are not existing yet and
    then return all the components."""
    print("[*] Adding puddles")
    for puddle in tqdm(puddles):
        print("[**] %s" % puddle)
        component.create(dci_context,
            puddle,
            component.PUDDLE,
            config['topic_id']
        )
    return json.loads(component.list(dci_context, config['topic_id']).text)


def inject_build_statuses(dcicontext, config, puddles, cache=None):
    dci = config['dci']
    jobdefinition_from_jenkins = jenkins_utils.get_jenkins_jobs(config)
    print('[*] Grabbed %d jobdefinitions from Jenkins'
          % len(jobdefinition_from_jenkins))

    jobdefinitions_from_dci = json.loads(
        dcijobdef.list(
            dcicontext, dci['topic_id']
        ).text
    )
    print('[*] Grabbed %d jobdefinitions from DCI CS'
          % len(jobdefinitions_from_dci['jobdefinitions']))

    dci_puddles = json.loads(
        component.list(dci_context, dci['topic_id'], where='type:puddle').text
    )
    print('[*] Grabbed %d puddles from DCI CS'
          % len(dci_puddles['components']))

    # Creating new jobdefinition in dci cs if they don't exist yet.
    print('[*] Creating %s potential new jobdefinitions in DCI'
          % len(jobdefinition_from_jenkins))
    with tqdm(len(jobdefinition_from_jenkins)) as pbar:
        for jdfj in jobdefinition_from_jenkins:
            pbar.update(1)
            # TODO(yassine): add unique integrity constraint to jodefinition's
            # names to get rid of this loop.
            for jobdef in jobdefinitions_from_dci['jobdefinitions']:
                if jobdef['name'] == jdfj['name']:
                    break
            else:
                # TODO(yassine): maybe adds the component types list
                dcijobdef.create(dcicontext, jdfj['name'], dci['topic_id'])

    # Parsing all logs to find puddles / status per build
    joblist = json.loads(dcijob.list(dci_context).text)
    all_jenkins_build_results = []
    for jd_from_jenkins in jobdefinition_from_jenkins:
        print('[*] Searching %s' % jd_from_jenkins['name'])
        builds = jenkins_utils.get_builds_from_job(jd_from_jenkins['url'])
        print('[*] %s builds found' % len(builds))
        for build in tqdm(builds):
            for jobdci in joblist['jobs']:
                if jobdci['comment'] == build['url']:
                    break
            else:
                puddle_ids = jenkins_utils.get_puddle_ids_from_build(
                    build, dci_puddles['components']
                )
                if puddle_ids:
                    all_jenkins_build_results.append({
                        'name': jd_from_jenkins['name'], 'puddles': puddle_ids,
                        'result': build['result'], 'url': build['url']
                    })
        print('[*] %s jenkins builds found' % len(all_jenkins_build_results))

    print('[*] Adding status found in DCI')

    # Update DCI jobdef list
    jobdefinitions_from_dci = json.loads(
        dcijobdef.list(
            dcicontext, dci['topic_id']
        ).text
    )

    # Parse all status to put the right jenkins
    # status in the right DCI jobstate
    all_job_comments = [jobit['comment'] for jobit in joblist['jobs']]
    for jenkins_build_result, myjobdef in itertools.product(
            tqdm(all_jenkins_build_results),
            jobdefinitions_from_dci['jobdefinitions']):
        if myjobdef['name'] == jenkins_build_result['name']:
            jobdefid = myjobdef['id']
        else:
            continue

        if jenkins_build_result['url'] in all_job_comments:
            continue

        new_dci_job = dcijob.create(dcicontext,
                                    recheck=False,
                                    remoteci_id=dci['remoteci_id'],
                                    team_id=dci['team_id'],
                                    jobdefinition_id=jobdefid,
                                    components=jenkins_build_result['puddles'],
                                    comment=jenkins_build_result['url']).text
        new_dci_job = json.loads(new_dci_job)

        jobstatus = jenkins_utils.get_job_status(jenkins_build_result['result'])
        state = dcijobstate.create(dci_context,
                                   status=jobstatus,
                                   comment=jenkins_build_result['url'],
                                   job_id=new_dci_job['job']['id']).text
        state = json.loads(state)

        nose_url = jenkins_utils.get_nosetests_url(jenkins_build_result['url'])
        if not nose_url:
            continue

        # maybe calculate the md5 of the file here can be a good idea
        args = [dcicontext, 'nosetests.xml',
                jenkins_utils.get_nosetests_content(jenkins_build_result['url'], nose_url),
                'application/junit', state['jobstate']['id']]
        dcifile.create(*args, job_id=new_dci_job['job']['id'])


if __name__ == '__main__':
    with open('config.yaml', 'r') as config_file:
        config = yaml.load(config_file)
    config_file.close()

    dci = config['dci']

    dci_context = dcicontext.build_dci_context(
        dci['control_server_url'], dci['login'], dci['password']
    )

    puddles = get_puddles_from_webserver(config['puddle']['url'])
    puddles = inject_puddles_in_dci_cs(dci, dci_context, puddles)
    inject_build_statuses(dci_context, config, puddles)
