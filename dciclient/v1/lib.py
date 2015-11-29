# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Red Hat, Inc
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

from dciclient.v1.handlers import componenttype
from dciclient.v1.handlers import job
from dciclient.v1.handlers import jobdefinition
from dciclient.v1.handlers import test
from dciclient.v1.handlers import remoteci

import requests

def get_http_session(dci_cs_url, login, password):
    session = requests.Session()
    session.headers.setdefault('Content-Type', 'application/json')
    session.auth = (login, password)
    session.dci_cs_url = dci_cs_url
    return session


def ensure_componenttype(session, componenttypes):
    """Ensure componenttype exist"""
    componenttype_ids = []

    for ct_name in componenttypes:
        l_componenttype = componenttype.ComponentType(session)
        #try:
        componenttype_ids.append(l_componenttype.create(name=ct_name).json()['componenttype']['id'])
        #except AlreadyExist:
        #    componenttype_ids.append(l_componenttype.show(name=ct_name).json()['id'])
        #    pass
        #except Exception e:
        #    raise e

    return componenttype_ids


def ensure_test(session, tests):
    """Ensure test exist"""
    test_ids = []

    for t_name in tests:
        l_test = test.Test(session)
        #try:
        test_ids.append(l_test.create(name=t_name).json()['test']['id'])
        #except AlreadyExist:
        #    test_ids.append(l_test.show(name=t_name).json()['id'])
        #    pass
        #except Exception e:
        #    raise e

    return test_ids


def create_jobdefinition(session, name, component, test):
    """Create an entry in JobDefinition"""
    l_jobdefinition = jobdefinition.JobDefinition(session)

    jobdefinition_id = l_jobdefinition.create(
        name=name,
        test_id=test,
    ).json()['jobdefinition']['id']

    l_jobdefinition.add_component(
        id=jobdefinition_id,
        component_id=component,
    )


def retrieve_remoteciid(session, remoteci_name):
    """Retrieve a remoteci id by its name"""
    l_remoteci = remoteci.RemoteCI(session)
    remotecis = l_remoteci.list().json()['remotecis']
 
    for rci in remotecis:
        if remoteci_name == rci['name']:
            remoteci_id = rci['id']
            break
 
    return remoteci_id
    

def retrieve_jobinformation(session, remoteci_id, team_id):
    """Retrieve job informations"""
    embedded = {
        'jobdefinition': 1,
        'jobdefinition.components': 1,
        'jobdefinition.components.componenttype': 1,
    }

    l_job = job.Job(session)
    job_id = l_job.create(recheck=False, remoteci_id=remoteci_id, team_id=team_id).json()

   
    return l_job.show(id=job_id, embedded=embedded).json()
