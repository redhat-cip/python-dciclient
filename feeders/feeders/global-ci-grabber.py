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


def create_jenkins_job_as_jobdefinition(topic_id, jenkins_job,
                                        dci_jobdefinitions):
    """Creating a new jobdefinition in dci cs from a jenkins job if it doesn't
    exist yet, return jobdefinition's id."""

    # TODO(yassine): add unique integrity constraint to jodefinition's
    # names to get rid of this loop.
    for dci_jd in dci_jobdefinitions['jobdefinitions']:
        if dci_jd['name'] == jenkins_jobs['name']:
            return dci_jd['id']
    else:
        new_jobdef = dcijobdef.create(dcicontext,
                                      jenkins_job['name'],
                                      topic_id)
        new_jobdef = json.loads(new_jobdef.text)
        return new_jobdef['jobdefinition']['id']


def create_puddles_as_components(config, dci_context, puddles):
    """Adds the new puddles in the DCI CS if they are not existing yet and
    then return all the components.
    """
    print("[*] Adding puddles")
    puddle_ids = []
    for puddle in tqdm(puddles):
        print("[**] puddle name: %s" % puddle['name'])
        new_component = component.create(
            dci_context,
            puddle['name'],
            puddle['type'],
            config['topic_id'],
            canonical_project_name="OSP-%s" % puddle['osp_version']
        )
        if new_component.status_code == 201:
            component_id = json.loads(new_component.text)['component']['id']
            puddle_ids.append(component_id)
        else:
            cmpt = component.get(dci_context, puddle['name'])
            component_id = json.loads(cmpt.text)['component']['id']
            puddle_ids.append(component_id)
    return puddle_ids


def create_dci_job(dcicontext, config, build, jjob_id, component_ids,
                   all_jobs_comments):
    """Create a new dci job which maps a jenkins build along with its
    puddles."""
    dci = config['dci']
    if build['url'] in all_jobs_comments:
        return

    new_dci_job = dcijob.create(dcicontext,
                                recheck=False,
                                remoteci_id=dci['remoteci_id'],
                                team_id=dci['team_id'],
                                jobdefinition_id=jjob_id,
                                components=component_ids,
                                comment=build['url']).text
    new_dci_job = json.loads(new_dci_job)

    status = jenkins_utils.get_job_status(build['result'])
    state = dcijobstate.create(dci_context,
                               status=status,
                               comment=build['url'],
                               job_id=new_dci_job['job']['id']).text
    state = json.loads(state)

    nose_url = jenkins_utils.get_nosetests_url(build['url'])
    if not nose_url:
        return

    # maybe calculate the md5 of the file here can be a good idea
    nosetests_content = jenkins_utils.get_nosetests_content(build['url'],
                                                            nose_url)
    dcifile.create(dcicontext,
                   'nosetests.xml',
                   nosetests_content,
                   'application/junit',
                   state['jobstate']['id'],
                   job_id=new_dci_job['job']['id'])

if __name__ == '__main__':
    with open('config.yaml', 'r') as config_file:
        config = yaml.load(config_file)
    config_file.close()

    dci = config['dci']

    dci_context = dcicontext.build_dci_context(
        dci['control_server_url'], dci['login'], dci['password']
    )

    # get all the jobdefinitions from dci cs
    jobdefinitions_from_dci = json.loads(
        dcijobdef.list(
            dcicontext, dci['topic_id']
        ).text
    )

    # get all the jobs components in order to track the build's urls
    jobs_from_dci = json.loads(dcijob.list(dci_context).text)['jobs']
    all_jobs_comments =  [j['comment'] for j in jobs_from_dci]

    jenkins_jobs = jenkins_utils.get_all_jobs(config)
    print('[*] Creating %s potential new jobdefinitions in DCI'
          % len(jenkins_jobs))

    for jjob in jenkins_jobs:
        # create the jobdefinition according to the jenkins job
        jjob_id = create_jenkins_job_as_jobdefinition(jjob,
                                                      jobdefinitions_from_dci)
        # retrieve all the builds from that jobs
        jenkins_builds = jenkins_utils.get_builds_from_job(jjob['url'])
        for build in jenkins_builds:
            # for each build, create the associated puddles as dci component
            puddles = jenkins_utils.get_puddles_from_jenkins_build(build)
            if len(puddles) < 2:
                print('[*] The build %s is lacking of puddles.' % build)
            component_ids = create_puddles_as_components(puddles)
            # finally create the dci job
            create_dci_job(jjob_id, build, component_ids, all_jobs_comments)
