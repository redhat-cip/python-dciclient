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
import sys
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

def create_jenkins_job_as_jobdefinition(dci_context, topic_id, jenkins_job,
                                        jobdefinitions_from_dci):
    """Creating a new jobdefinition in dci cs from a jenkins job if it doesn't
    exist yet, return jobdefinition's id.
    """

    # TODO(yassine): add unique integrity constraint to jodefinition's
    # names to get rid of this loop.
    for dci_jd in jobdefinitions_from_dci['jobdefinitions']:
        if dci_jd['name'] == jenkins_job['name']:
            return dci_jd['id']
    else:
        new_jobdef = dcijobdef.create(dci_context,
                                      jenkins_job['name'],
                                      topic_id)
        new_jobdef = json.loads(new_jobdef.text)
        return new_jobdef['jobdefinition']['id']


def create_puddles_as_components(dci_context, topic_id, puddles):
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
            topic_id,
            canonical_project_name="OSP-%s" % puddle['osp_version'],
            data={'feeder': 'global-status-grabber'}
        )
        if new_component.status_code == 201:
            component_id = json.loads(new_component.text)['component']['id']
            puddle_ids.append(component_id)
        else:
            cmpt = component.get(dci_context, puddle['name'])
            component_id = json.loads(cmpt.text)['component']['id']
            puddle_ids.append(component_id)
    return puddle_ids


def create_dci_job(dci_context, team_id, remoteci_id, build, jjob_id,
                   component_ids, all_jobs_comments):
    """Create a new dci job which maps a jenkins build along with its
    puddles.
    """
    if build['url'] in all_jobs_comments:
        return

    new_dci_job = dcijob.create(dci_context,
                                recheck=False,
                                remoteci_id=remoteci_id,
                                team_id=team_id,
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
    dcifile.create(dci_context,
                   'nosetests.xml',
                   nosetests_content,
                   'application/junit',
                   state['jobstate']['id'],
                   job_id=new_dci_job['job']['id'])

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as config_file:
        config = yaml.load(config_file)

    dci = config['dci']

    dci_context = dcicontext.build_dci_context(
        dci['control_server_url'], dci['login'], dci['password']
    )

    # get all the jobdefinitions from dci cs
    jobdefinitions_from_dci = json.loads(
        dcijobdef.list(
            dci_context, dci['topic_id']
        ).text
    )

    # get all the jobs components in order to track the build's urls
    jobs_from_dci = json.loads(dcijob.list(dci_context).text)['jobs']
    all_jobs_comments = [j['comment'] for j in jobs_from_dci]

    all_jenkins_jobs = jenkins_utils.get_all_jobs(config)
    print('[*] Creating %s potential new jobdefinitions in DCI'
          % len(all_jenkins_jobs))

    for jjob in tqdm(all_jenkins_jobs):
        # create the jobdefinition according to the jenkins job
        print('[*] Create jenkins job %s as jobdefinition' % jjob['name'])
        jjob_id = create_jenkins_job_as_jobdefinition(dci_context,
                                                      dci['topic_id'], jjob,
                                                      jobdefinitions_from_dci)
        # retrieve all the builds from that job
        jenkins_builds = jenkins_utils.get_builds_from_job(jjob['url'])
        for build in tqdm(jenkins_builds):
            # for each build, create the associated puddles as dci component
            puddles = jenkins_utils.get_puddles_from_jenkins_build(build)
            if len(puddles) < 2:
                print('[*] The build %s is lacking of puddles.' % build)
                sys.exit(1)
            component_ids = create_puddles_as_components(dci_context,
                                                         dci['topic_id'],
                                                         puddles)
            # finally create the dci job
            print('[*] Creating a new dci job.')
            create_dci_job(dci_context, dci['team_id'], dci['remoteci_id'],
                           build, jjob_id, component_ids, all_jobs_comments)
