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

from dci.server.tests import conftest as server_conftest
from dciclient import v1 as dci_client
from dciclient.v1 import dciclientlib as dci_clientlib
from dciclient.v1.shell_commands import _get_http_session
from dciclient.v1.shell_commands import cli
from dciclient.v1.tests import utils

import click
import pytest


@pytest.fixture(autouse=True, scope='module')
def remove_decorators():
    noop = lambda f: f
    cli.command = lambda *args, **kwargs: noop
    click.option = lambda *args, **kwargs: noop
    click.pass_obj = noop


@pytest.fixture(scope='session')
def engine(request):
    return server_conftest.engine(request)


@pytest.fixture
def server(engine):
    return server_conftest.app(engine)


@pytest.fixture
def db_clean(request, server):
    return server_conftest.db_clean(request, server)


@pytest.fixture
def db_provisioning(server, db_clean):
    server_conftest.db_provisioning(server, db_clean)


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
def http_session(server, db_provisioning):
    session = _get_http_session('http://dci_server.com', 'admin', 'admin')
    flask_adapter = utils.FlaskHTTPAdapter(server.test_client())
    session.mount('http://dci_server.com', flask_adapter)
    return session


@pytest.fixture
def client_v1(server, db_provisioning):
    client = dci_clientlib.DCIClient(
        end_point='http://dci_server.com/api/v1',
        login='admin', password='admin'
    )
    flask_adapter = utils.FlaskHTTPAdapter(server.test_client())
    client._s.mount('http://dci_server.com/api/v1', flask_adapter)
    return client
