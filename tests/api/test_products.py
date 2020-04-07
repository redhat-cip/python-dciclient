# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Red Hat, Inc
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

from dciclient.v1.api import product


def test_success_create_product_authorized(dci_context):
    """Create a product."""

    products_original_cnt = product.list(dci_context).json()["_meta"]["count"]
    product.create(dci_context, "OpenStack")
    products_test = product.list(dci_context).json()
    products_test_cnt = products_test["_meta"]["count"]

    assert products_test_cnt == products_original_cnt + 1
    assert "OpenStack" in [prod["name"] for prod in products_test["products"]]


def test_failure_create_product_unauthorized(dci_context_user_admin):
    """Fail to create a product with an unauthorized identity."""

    result = product.create(dci_context_user_admin, "OpenStack")

    assert result.status_code == 401


def test_success_list_all_products(dci_context, product_id):
    """List all products."""

    products_original_cnt = product.list(dci_context).json()["_meta"]["count"]
    product.create(dci_context, "OpenStack")
    products_test = product.list(dci_context).json()
    products_test_cnt = products_test["_meta"]["count"]

    assert products_test_cnt == products_original_cnt + 1
    assert product_id in [prod["id"] for prod in products_test["products"]]
    assert "OpenStack" in [prod["name"] for prod in products_test["products"]]


def test_success_show_product(dci_context, product_id):
    """Retrieve a specific product."""

    product_to_retrieve = product.get(dci_context, product_id).json()

    assert product_id == product_to_retrieve["product"]["id"]


def test_success_update_product_authorized(dci_context, product_id):
    """Update a specific product."""

    product_to_retrieve = product.get(dci_context, product_id).json()
    product_etag = product_to_retrieve["product"]["etag"]

    updated_params = {"description": "This is a new description"}
    product.update(dci_context, product_id, etag=product_etag, **updated_params)

    product_to_retrieve = product.get(dci_context, product_id).json()

    assert "This is a new description" == product_to_retrieve["product"]["description"]


def test_failure_update_product_unauthorized(
    dci_context, dci_context_user_admin, product_id
):
    """Fail to update a product with an unauthorized identity."""

    product_to_retrieve = product.get(dci_context, product_id).json()
    product_etag = product_to_retrieve["product"]["etag"]

    updated_params = {"description": "This is a new description"}
    result = product.update(
        dci_context_user_admin, product_id, etag=product_etag, **updated_params
    )

    assert result.status_code == 401


def test_success_delete_product_authorized(dci_context, product_id):
    """Delete a product that belongs."""

    product_to_retrieve = product.get(dci_context, product_id).json()
    product_etag = product_to_retrieve["product"]["etag"]

    products_original_cnt = product.list(dci_context).json()["_meta"]["count"]
    product.delete(dci_context, product_id, etag=product_etag)
    products_test = product.list(dci_context).json()
    products_test_cnt = products_test["_meta"]["count"]

    assert products_test_cnt == products_original_cnt - 1
    assert product_id not in [prod["id"] for prod in products_test["products"]]


def test_failure_delete_product_unauthorized(
    dci_context, dci_context_user_admin, product_id
):
    """Fail to delete a product that belongs."""

    product_to_retrieve = product.get(dci_context, product_id).json()
    product_etag = product_to_retrieve["product"]["etag"]

    result = product.delete(dci_context_user_admin, product_id, etag=product_etag)

    assert result.status_code == 401
