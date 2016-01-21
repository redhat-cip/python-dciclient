# -*- encoding: utf-8 -*-
#
# Copyright 2015 Red Hat, Inc.
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

import dci.tests.conftest as server_conftest
from dciclient.v1.api import component
from dciclient.v1.api import context
from dciclient.v1.api import job
from dciclient.v1.api import jobdefinition
from dciclient.v1.api import remoteci
from dciclient.v1.api import team
from dciclient.v1.api import test


from dciclient import v1 as dci_client

import click.testing
import dciclient.shell as shell
from dciclient.v1.tests.shell_commands import utils
import functools
import pytest


@pytest.fixture(scope='session')
def engine(request):
    return server_conftest.engine(request)


@pytest.fixture
def db_clean(request, engine):
    return server_conftest.db_clean(request, engine)


@pytest.fixture
def db_provisioning(db_clean, engine):
    server_conftest.db_provisioning(db_clean, engine)


@pytest.fixture
def server(db_provisioning, engine):
    return server_conftest.app(db_provisioning, engine)


@pytest.fixture
def client(server, db_provisioning):
    client = dci_client.DCIClient(
        end_point='http://dci_server.com/api',
        login='admin', password='admin'
    )
    flask_adapter = utils.FlaskHTTPAdapter(server.test_client())
    client.s.mount('http://dci_server.com', flask_adapter)
    return client


@pytest.fixture
def dci_context(server, db_provisioning):
    test_context = context.DciContext('http://dci_server.com',
                                      'admin', 'admin')
    flask_adapter = utils.FlaskHTTPAdapter(server.test_client())
    test_context.session.mount('http://dci_server.com', flask_adapter)
    return test_context


@pytest.fixture
def runner(dci_context):
    context.build_dci_context = lambda **kwargs: dci_context
    runner = click.testing.CliRunner(env={'DCI_LOGIN': '', 'DCI_PASSWORD': '',
                                          'DCI_CLI_OUTPUT_FORMAT': 'json'})
    runner.invoke = functools.partial(runner.invoke, shell.main)
    return runner


@pytest.fixture
def team_id(dci_context):
    return team.create(dci_context, name='tname').json()['team']['id']


@pytest.fixture
def job_id(dci_context):
    my_team = team.create(dci_context, name='tname').json()['team']
    my_remoteci = remoteci.create(dci_context,
                                  name='tname', team_id=my_team['id'],
                                  data={'remoteci': 'remoteci'}).json()
    my_remoteci_id = my_remoteci['remoteci']['id']
    my_test = test.create(
        dci_context, name='tname', data={'test': 'test'}).json()
    my_test_id = my_test['test']['id']
    my_jobdefinition = jobdefinition.create(
        dci_context, name='tname', test_id=my_test_id).json()
    my_component = component.create(
        dci_context, name='hihi', type='git_review',
        data={'component': 'component'}).json()
    my_component_id = my_component['component']['id']
    jobdefinition.add_component(dci_context,
                                my_jobdefinition['jobdefinition']['id'],
                                my_component_id)
    my_job = job.schedule(dci_context, my_remoteci_id).json()
    return my_job['job']['id']
