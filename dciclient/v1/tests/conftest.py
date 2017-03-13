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

import dci
import dci.app
import dci.common.utils as dci_utils
import dci.dci_config

import dciclient.shell as shell
import dciclient.v1 as dci_client
import dciclient.v1.api as api
import dciclient.v1.tests.shell_commands.utils as utils

import pytest
import sqlalchemy
import sqlalchemy_utils.functions


import click.testing
import functools
import json
import os
import passlib.apps as passlib_apps


class mocked_store_engine(object):
    files = {}

    def delete(self, filename):
        del(self.files[filename])

    def get(self, filename):
        with open('/tmp/swift/' + filename, 'r') as fd:
            return [None, fd.read()]

    def head(self, filename):
        return self.files[filename]

    def upload(self, filename, iterable, pseudo_folder=None,
               create_container=True):
        file_path = '/tmp/swift/' + filename
        os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'wb') as fd:
            fd.write(iterable)
        self.files[filename] = {
            'etag': 'boby',
            'content-type': 'application/octet-stream',
            'content-length': os.stat(file_path).st_size}


@pytest.fixture(scope='session')
def engine(request):
    def mocked_get_store():
        return mocked_store_engine()

    dci.dci_config.get_store = mocked_get_store
    conf = dci.dci_config.generate_conf()
    db_uri = conf['SQLALCHEMY_DATABASE_URI']

    engine = sqlalchemy.create_engine(db_uri)

    def del_db():
        if sqlalchemy_utils.functions.database_exists(db_uri):
            sqlalchemy_utils.functions.drop_database(db_uri)

    del_db()
    request.addfinalizer(del_db)
    sqlalchemy_utils.functions.create_database(db_uri)

    dci.db.models.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_clean(request, engine):
    def fin():
        for table in reversed(dci.db.models.metadata.sorted_tables):
            engine.execute(table.delete())
    request.addfinalizer(fin)


@pytest.fixture(scope='session', autouse=True)
def memoize_password_hash():
    pwd_context = passlib_apps.custom_app_context
    pwd_context.verify = dci_utils.memoized(pwd_context.verify)
    pwd_context.encrypt = dci_utils.memoized(pwd_context.encrypt)


@pytest.fixture
def db_provisioning(db_clean, engine):
    with engine.begin() as conn:
        utils.provision(conn)


@pytest.fixture
def server(db_provisioning, engine):
    app = dci.app.create_app(dci.dci_config.generate_conf())
    app.testing = True
    app.engine = engine
    return app


@pytest.fixture
def client(server, db_provisioning):
    client = dci_client.DCIClient(
        end_point='http://dciserver.com/api',
        login='admin', password='admin'
    )
    flask_adapter = utils.FlaskHTTPAdapter(server.test_client())
    client.s.mount('http://dciserver.com', flask_adapter)
    return client


@pytest.fixture
def dci_context(server, db_provisioning):
    test_context = api.context.DciContext('http://dciserver.com',
                                          'admin', 'admin')
    flask_adapter = utils.FlaskHTTPAdapter(server.test_client())
    test_context.session.mount('http://dciserver.com', flask_adapter)
    return test_context


@pytest.fixture
def dci_context_other_user_agent(server, db_provisioning):
    test_context = api.context.DciContext('http://dciserver.com',
                                          'admin', 'admin',
                                          user_agent='myagent-0.1')
    flask_adapter = utils.FlaskHTTPAdapter(server.test_client())
    test_context.session.mount('http://dciserver.com', flask_adapter)
    return test_context


@pytest.fixture
def dci_context_broken(server, db_provisioning):
    test_context = api.context.DciContext('http://no_where.com',
                                          'admin', 'admin')
    test_context.last_jobstate_id = 1
    test_context.last_job_id = 1
    return test_context


@pytest.fixture
def runner(dci_context):
    api.context.build_dci_context = lambda **kwargs: dci_context
    runner = click.testing.CliRunner(env={'DCI_LOGIN': '', 'DCI_PASSWORD': '',
                                          'DCI_CLI_OUTPUT_FORMAT': 'json'})
    invoke_raw = functools.partial(runner.invoke, shell.main)

    def invoke_json(*kargs):
        r = invoke_raw(*kargs)
        try:
            return json.loads(r.output)
        except ValueError as e:
            print('Failed to JSON decode: >>%s<<' % r.output)
            print('Exit code was: %d' % r.exit_code)
            raise e

    def invoke_raw_parse(*kargs):
        r = invoke_raw(['--format', 'table'] + kargs[0])
        if r.exit_code != 0:
            return r.output
        fields = r.output.split('\n')[1].split('|')
        # NOTE(Gonéri): we only return the very first row because
        # there is no way to know if it a multi-line result
        data = r.output.split('\n')[3].split('|')
        fields = [i.lstrip(' ').rstrip(' ') for i in fields[1:-1]]
        data = [i.lstrip(' ').rstrip(' ') for i in data[1:]]
        result = {}
        for f in fields:
            result[f] = data.pop(0)
        return result

    runner.invoke = invoke_json
    runner.invoke_raw = invoke_raw
    runner.invoke_raw_parse = invoke_raw_parse
    return runner


@pytest.fixture
def team_id(dci_context):
    return api.team.create(dci_context, name='tname').json()['team']['id']


@pytest.fixture
def topic_id(dci_context):
    kwargs = {'name': 'foo_topic'}
    return api.topic.create(dci_context, **kwargs).json()['topic']['id']


@pytest.fixture
def test_id(dci_context, team_id):
    kwargs = {'name': 'test_name', 'team_id': team_id}
    return api.test.create(dci_context, **kwargs).json()['test']['id']


@pytest.fixture
def components(dci_context, topic_id):
    component1 = {'name': 'component1',
                  'type': 'git_commit',
                  'data': {},
                  'canonical_project_name': 'component 1',
                  'topic_id': topic_id}

    component2 = {'name': 'component2',
                  'type': 'git_commit',
                  'data': {},
                  'canonical_project_name': 'component 2',
                  'topic_id': topic_id}

    return [component1, component2]


@pytest.fixture
def remoteci_id(dci_context, team_id):
    kwargs = {'name': 'remoteci',
              'team_id': team_id,
              'data': {'remoteci': 'remoteci'}}
    rci = api.remoteci.create(dci_context, **kwargs).json()
    return rci['remoteci']['id']


@pytest.fixture
def component_id(dci_context, topic_id):
    kwargs = {'name': 'component1', 'type': 'git_review',
              'data': {'component': 'component'}, 'topic_id': topic_id}

    component = api.component.create(dci_context, **kwargs).json()
    return component['component']['id']


@pytest.fixture
def job_factory(dci_context, team_id, topic_id, remoteci_id):
    def create():
        job = api.job.schedule(dci_context, remoteci_id, topic_id).json()
        job_id = job['job']['id']
        api.file.create(dci_context, name='res_junit.xml',
                        content=JUNIT, mime='application/junit',
                        job_id=job_id)
        jobstate_id = api.jobstate.create(
            dci_context, 'pre-run', 'starting',
            job_id).json()['jobstate']['id']
        api.file.create(dci_context, name='pre-run',
                        content='pre-run ongoing', mime='plain/text',
                        jobstate_id=jobstate_id)
        jobstate_id = api.jobstate.create(
            dci_context, 'running', 'starting the build',
            job_id).json()['jobstate']['id']
        return job

    JUNIT = """
    <testsuite errors="0" failures="0" name="pytest" skips="1"
               tests="3" time="46.050">
    <properties>
      <property name="x" value="y" />
      <property name="a" value="b" />
    </properties>
    <testcase classname="" file="test-requirements.txt"
              name="test-requirements.txt" time="0.0109479427338">
        <skipped message="all tests skipped by +SKIP option"
                 type="pytest.skip">Skipped for whatever reasons</skipped>
    </testcase>
    <testcase classname="tests.test_app" file="tests/test_app.py" line="26"
              name="test_cors_preflight" time="2.91562318802"/>
    <testcase classname="tests.test_app" file="tests/test_app.py" line="42"
              name="test_cors_headers" time="0.574683904648"/>
    </testsuite>"""

    kwargs = {'name': 'hihi', 'type': 'type_1', 'topic_id': topic_id,
              'data': {'component': 'component1'}}
    api.component.create(dci_context, **kwargs).json()

    kwargs = {'name': 'haha', 'type': 'type_2', 'topic_id': topic_id,
              'data': {'component': 'component2'}}
    api.component.create(dci_context, **kwargs).json()

    kwargs = {'name': 'tname', 'topic_id': topic_id,
              'component_types': ['type_1', 'type_2']}
    api.jobdefinition.create(dci_context, **kwargs).json()

    api.topic.attach_team(dci_context, topic_id, team_id)
    return create


@pytest.fixture
def job_id(job_factory):
    return job_factory()['job']['id']


@pytest.fixture
def file_id(dci_context, job_id):
    return api.file.list(dci_context).json()['files'][-1]['id']


@pytest.fixture
def jobstate_id(dci_context, job_id):
    kwargs = {'job_id': job_id, 'status': 'running', 'comment': 'some comment'}
    jobstate = api.jobstate.create(dci_context, **kwargs).json()
    return jobstate['jobstate']['id']
