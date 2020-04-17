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

import pytest
import sqlalchemy
import sqlalchemy_utils.functions
import os
import passlib.apps as passlib_apps

import dci
import dci.app
import dci.dci_config
from dciclient.v1.api import context as api_context
from dciclient.v1.api import team as api_team
from dciclient.v1.api import user as api_user
from dciclient.v1.api import product as api_product
from dciclient.v1.api import remoteci as api_remoteci
from dciclient.v1.api import component as api_component
from dciclient.v1.api import file as api_file
from dciclient.v1.api import topic as api_topic
from dciclient.v1.api import job as api_job
from dciclient.v1.api import jobstate as api_jobstate
from dciclient.v1.api import test as api_test
from dciclient.v1.api import base as api_base
from dciclient.v1.shell_commands import runner as dci_runner
from dciclient.v1.shell_commands import cli
from tests.shell_commands import utils


class Mocked_store_engine(object):
    files = {}

    def __init__(self, conf):
        self.container = conf

    def delete(self, filename):
        del self.files[filename]

    def get(self, filename):
        fd = open("/tmp/swift/" + filename, "r")
        return [None, fd]

    # TODO(Goneri): should be dropped once
    # I9804796987e05417dcc20a1099b4a26db4f9f1f2 is merged
    def get_object(self, filename):
        _, fd = self.get(filename)
        return fd.read()

    def head(self, filename):
        return self.files[filename]

    def upload(self, filename, iterable, pseudo_folder=None, create_container=True):
        file_path = "/tmp/swift/" + filename
        if not os.path.isdir(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, "wb") as fd:
            if hasattr(iterable, "read"):
                fd.write(iterable.read())
            else:
                fd.write(iterable)
        self.files[filename] = {
            "etag": "boby",
            "content-type": "application/octet-stream",
            "content-length": os.stat(file_path).st_size,
        }

    def build_file_path(self, root, middle, file_id):
        root = str(root)
        middle = str(middle)
        file_id = str(file_id)
        return "%s/%s/%s" % (root, middle, file_id)


@pytest.fixture(scope="session")
def engine(request):
    def mocked_get_store(conf):
        store = Mocked_store_engine(conf)
        return store

    dci.dci_config.get_store = mocked_get_store
    conf = dci.dci_config.generate_conf()
    db_uri = conf["SQLALCHEMY_DATABASE_URI"]

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
def db_provisioning(db_clean, engine):
    with engine.begin() as conn:
        utils.provision(conn)


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
    url="http://dciserver.com",
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
    url="http://dciserver.com",
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

    def invoke_raw(arguments):
        environment = {}
        args = cli.parse_arguments(arguments, environment)
        return dci_runner.run(context, args)

    class Runner(object):
        pass

    runner = Runner()
    runner.invoke = invoke
    runner.invoke_raw = invoke_raw
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
    user = api_user.list(dci_context, where="name:user")
    return user.json()["users"][0]["team_id"]


@pytest.fixture
def product_id(dci_context, team_id):
    return api_product.create(dci_context, name="myproduct").json()["product"]["id"]


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
def test_id(dci_context, team_id):
    kwargs = {"name": "test_name", "team_id": team_id}
    return api_test.create(dci_context, **kwargs).json()["test"]["id"]


@pytest.fixture
def test_user_id(dci_context, team_user_id):
    kwargs = {"name": "test_user_name", "team_id": team_user_id}
    return api_test.create(dci_context, **kwargs).json()["test"]["id"]


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
    }

    component = api_component.create(dci_context, **kwargs).json()
    return component["component"]["id"]


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
def test_user(runner, team_user_id):
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
            "--team-id",
            team_user_id,
        ]
    )["user"]


@pytest.fixture
def team_test(dci_context, team_id):
    test = api_test.create(dci_context, "sometest", team_id=team_id).json()
    return test["test"]


@pytest.fixture
def feeder(dci_context, team_id):
    kwargs = {"name": "feeder", "team_id": team_id, "state": "active"}
    feeder = api_base.create(dci_context, "feeders", **kwargs).json()
    return feeder["feeder"]
