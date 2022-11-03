# -*- encoding: utf-8 -*-
#
# Copyright 2015-2022 Red Hat, Inc.
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

import pytest
import sqlalchemy
import sqlalchemy_utils.functions
import passlib.apps as passlib_apps
from sqlalchemy.orm import sessionmaker

import dci
import dci.app
import dci.dci_config
from dciclient import create_component as dci_create_component
from dciclient import diff_jobs as dci_diff_jobs
from dciclient import find_latest_component as dci_find_latest_component
from dciclient.v1.api import context as api_context
from dciclient.v1.api import team as api_team
from dciclient.v1.api import product as api_product
from dciclient.v1.api import remoteci as api_remoteci
from dciclient.v1.api import component as api_component
from dciclient.v1.api import file as api_file
from dciclient.v1.api import topic as api_topic
from dciclient.v1.api import job as api_job
from dciclient.v1.api import jobstate as api_jobstate
from dciclient.v1.api import base as api_base
from dciclient.v1.shell_commands import runner as dci_runner
from dciclient.v1.shell_commands import cli
from tests.shell_commands import utils


@pytest.fixture(scope="session")
def engine(request):
    conf = dci.dci_config.generate_conf()
    db_uri = conf["SQLALCHEMY_DATABASE_URI"]

    engine = sqlalchemy.create_engine(db_uri)

    def del_db():
        if sqlalchemy_utils.functions.database_exists(db_uri):
            sqlalchemy_utils.functions.drop_database(db_uri)

    del_db()
    request.addfinalizer(del_db)
    sqlalchemy_utils.functions.create_database(db_uri)

    dci.db.models2.Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def empty_db(request, engine):
    def fin():
        for table in reversed(dci.db.models2.Base.metadata.sorted_tables):
            engine.execute(table.delete())

    request.addfinalizer(fin)


@pytest.fixture(scope="session", autouse=True)
def memoize_password_hash():
    def memoize(func):
        cache = {}

        def helper(*args):
            if args in cache:
                return cache[args]
            else:
                value = func(*args)
                cache[args] = value
                return value

        return helper

    pwd_context = passlib_apps.custom_app_context
    pwd_context.verify = memoize(pwd_context.verify)
    pwd_context.encrypt = memoize(pwd_context.encrypt)


@pytest.fixture
def session(engine):
    return sessionmaker(bind=engine)()


@pytest.fixture
def db_provisioning(empty_db, session):
    utils.provision(session)


@pytest.fixture
def server(db_provisioning, engine):
    app = dci.app.create_app(dci.dci_config.generate_conf())
    app.testing = True
    app.engine = engine
    return app


def context_factory(
    server,
    db_provisioning,
    login,
    password,
    url="http://localhost",
    user_agent=None,
):
    extras = {}
    if user_agent:
        extras["user_agent"] = user_agent
    test_context = api_context.DciContext(url, login, password, **extras)
    flask_adapter = utils.FlaskHTTPAdapter(server.test_client())
    test_context.session.mount(url, flask_adapter)
    return test_context


@pytest.fixture
def dci_context(server, db_provisioning):
    return context_factory(server, db_provisioning, "admin", "admin")


@pytest.fixture
def dci_context_user_admin(server, db_provisioning):
    return context_factory(server, db_provisioning, "user_admin", "user_admin")


@pytest.fixture
def dci_context_user(server, db_provisioning):
    return context_factory(server, db_provisioning, "user", "user")


@pytest.fixture
def dci_context_test_user(server, db_provisioning, test_user):
    return context_factory(server, db_provisioning, "foo", "pass")


@pytest.fixture
def dci_context_product_owner(server, db_provisioning):
    return context_factory(server, db_provisioning, "product_owner", "product_owner")


@pytest.fixture
def dci_context_other_user_agent(server, db_provisioning):
    return context_factory(
        server, db_provisioning, "admin", "admin", user_agent="myagent-0.1"
    )


@pytest.fixture
def dci_context_broken(server, db_provisioning):
    test_context = api_context.DciContext("http://no_where.com", "admin", "admin")
    test_context.last_job_id = 1
    return test_context


@pytest.fixture
def signature_context_factory(
    server,
    db_provisioning,
    client_id=None,
    api_secret=None,
    url="http://localhost",
    user_agent=None,
):
    def f(
        server=server,
        db_provisioning=db_provisioning,
        client_id=client_id,
        api_secret=api_secret,
        url=url,
        user_agent=user_agent,
    ):
        extras = {}
        if user_agent:
            extras["user_agent"] = user_agent
        test_context = api_context.DciSignatureContext(url, client_id, api_secret)
        flask_adapter = utils.FlaskHTTPAdapter(server.test_client())
        test_context.session.mount(url, flask_adapter)
        return test_context

    return f


def runner_factory(context):
    def invoke(arguments):
        environment = {}
        args = cli.parse_arguments(arguments, environment)
        response = dci_runner.run(context, args)
        return response.json() if response else None

    def invoke_create_component(arguments):
        environment = {}
        args = dci_create_component.parse_arguments(arguments, environment)
        response = dci_create_component.run(context, args)
        return response.json() if response else None

    def invoke_find_latest_component(arguments):
        environment = {}
        args = dci_find_latest_component.parse_arguments(arguments, environment)
        response = dci_find_latest_component.run(context, args)
        return response

    def invoke_diff_jobs(arguments):
        environment = {}
        args = dci_diff_jobs.parse_arguments(arguments, environment)
        return dci_diff_jobs.run(context, args)

    def invoke_raw(arguments):
        environment = {}
        args = cli.parse_arguments(arguments, environment)
        return dci_runner.run(context, args)

    class Runner(object):
        pass

    runner = Runner()
    runner.invoke = invoke
    runner.invoke_raw = invoke_raw
    runner.invoke_create_component = invoke_create_component
    runner.invoke_find_latest_component = invoke_find_latest_component
    runner.invoke_diff_jobs = invoke_diff_jobs
    return runner


@pytest.fixture
def runner(dci_context):
    return runner_factory(dci_context)


@pytest.fixture
def runner_user_admin(dci_context_user_admin):
    return runner_factory(dci_context_user_admin)


@pytest.fixture
def runner_user(dci_context_user):
    return runner_factory(dci_context_user)


@pytest.fixture
def dci_context_remoteci(
    server, db_provisioning, remoteci_id, signature_context_factory, remoteci_api_secret
):
    return signature_context_factory(
        client_id=remoteci_id, api_secret=remoteci_api_secret
    )


@pytest.fixture
def runner_remoteci(dci_context_remoteci):
    return runner_factory(dci_context_remoteci)


@pytest.fixture
def team_id(dci_context):
    return api_team.create(dci_context, name="tname").json()["team"]["id"]


@pytest.fixture
def team_admin_id(dci_context):
    return api_team.list(dci_context, where="name:admin").json()["teams"][0]["id"]


@pytest.fixture
def team_user_id(dci_context):
    user = api_team.list(dci_context, where="name:user")
    return user.json()["teams"][0]["id"]


@pytest.fixture
def team_user_name(dci_context):
    user = api_team.list(dci_context, where="name:user")
    return user.json()["teams"][0]["name"]


@pytest.fixture
def product_id(dci_context, team_id):
    return api_product.list(
        dci_context,
        where="name:dci_product").json()["products"][0]['id']


@pytest.fixture
def product(dci_context, product_id):
    return api_product.get(dci_context, product_id).json()["product"]


@pytest.fixture
def topic_id(dci_context, product_id):
    kwargs = {
        "name": "foo_topic",
        "component_types": ["type_1", "type_2"],
        "product_id": product_id,
        "export_control": False,
    }
    return api_topic.create(dci_context, **kwargs).json()["topic"]["id"]


@pytest.fixture
def topic(dci_context, product_id):
    kwargs = {
        "name": "bar_topic",
        "component_types": ["type_1", "type_2"],
        "product_id": product_id,
        "export_control": False,
    }
    return api_topic.create(dci_context, **kwargs).json()["topic"]["name"]


@pytest.fixture
def remoteci_id(dci_context, team_user_id):
    kwargs = {
        "name": "remoteci",
        "team_id": team_user_id,
        "data": {"remoteci": "remoteci"},
    }
    rci = api_remoteci.create(dci_context, **kwargs).json()
    return rci["remoteci"]["id"]


@pytest.fixture
def remoteci_api_secret(dci_context, remoteci_id):
    rci = api_remoteci.get(dci_context, remoteci_id).json()
    return rci["remoteci"]["api_secret"]


@pytest.fixture
def component_id(dci_context, topic_id):
    kwargs = {
        "name": "component1",
        "type": "git_review",
        "data": {"component": "component"},
        "topic_id": topic_id,
        "tags": ["tag1", "tag2"],
    }

    component = api_component.create(dci_context, **kwargs).json()
    return component["component"]["id"]


@pytest.fixture
def component(dci_context, component_id):
    return api_component.get(dci_context, component_id).json()["component"]


@pytest.fixture
def components_ids(dci_context, topic_id):
    ids = []
    kwargs = {
        "name": "component1",
        "type": "type_1",
        "data": {"component": "component"},
        "topic_id": topic_id,
    }

    component = api_component.create(dci_context, **kwargs).json()
    ids.append(component["component"]["id"])
    kwargs["name"] = "component2"
    kwargs["type"] = "type_2"
    component = api_component.create(dci_context, **kwargs).json()
    ids.append(component["component"]["id"])
    return ids


@pytest.fixture
def job_factory(
    dci_context,
    dci_context_remoteci,
    team_user_id,
    remoteci_id,
    topic_id,
    components_ids,
):
    def create():
        job = api_job.schedule(dci_context_remoteci, topic_id).json()
        job_id = job["job"]["id"]
        api_file.create(
            dci_context_remoteci,
            name="res_junit.xml",
            content=JUNIT,
            mime="application/junit",
            job_id=job_id,
        )
        jobstate_id = api_jobstate.create(
            dci_context_remoteci, "pre-run", "starting", job_id
        ).json()["jobstate"]["id"]
        api_file.create(
            dci_context_remoteci,
            name="pre-run",
            content="pre-run ongoing",
            mime="plain/text",
            jobstate_id=jobstate_id,
        )
        api_jobstate.create(
            dci_context_remoteci, "running", "starting the build", job_id
        )
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

    api_topic.attach_team(dci_context, topic_id, team_user_id)
    return create


@pytest.fixture
def job_id(job_factory, components_ids):
    return job_factory()["job"]["id"]


@pytest.fixture
def job(job_factory):
    return job_factory()["job"]


@pytest.fixture
def file_id(dci_context, job_id):
    return api_job.list_files(dci_context, id=job_id).json()["files"][-1]["id"]


@pytest.fixture
def jobstate_id(dci_context, job_id):
    kwargs = {"job_id": job_id, "status": "running", "comment": "some comment"}
    jobstate = api_jobstate.create(dci_context, **kwargs).json()
    return jobstate["jobstate"]["id"]


@pytest.fixture
def test_user(runner):
    return runner.invoke(
        [
            "user-create",
            "--name",
            "foo",
            "--email",
            "foo@example.org",
            "--fullname",
            "Foo Bar",
            "--password",
            "pass",
        ]
    )["user"]


@pytest.fixture
def feeder(dci_context, team_id):
    kwargs = {"name": "feeder", "team_id": team_id, "state": "active"}
    feeder = api_base.create(dci_context, "feeders", **kwargs).json()
    return feeder["feeder"]
