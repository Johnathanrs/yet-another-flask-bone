#!/usr/bin/env python

import json
import random
from unittest.mock import patch

import pytest

from easybiodata.tests.utils.helpers import random_user_on_team
from easybiodata.tests.utils.request_helpers import login_as_user


@pytest.fixture(scope='session')
def flask_app():
    from flask import request
    from application import application as app

    @app.before_request
    def print_request():
        j = request.get_json(silent=True)
        print('{} {}\n{}'.format(request.method,
                                 request.url,
                                 json.dumps(j) if j is not None else 'None'))

    @app.after_request
    def print_response(response):
        if response.content_type == 'application/json':
            print(str(response.data, encoding='utf8'))
        return response

    return app


@pytest.fixture(scope='function')
def test_client(flask_app):
    return flask_app.test_client()


@pytest.fixture(scope='function', autouse=True)
def app_context(flask_app, request):
    app_context = flask_app.app_context()
    app_context.push()
    request.addfinalizer(app_context.pop)


@pytest.fixture(scope='function', autouse=True)
def geocode_address_mock(request):
    contacts = set()

    def geocode(service, contact):
        contacts.add(contact)

    patcher = patch('easybiodata.contacts.ContactService.geocode_address', geocode)
    mock = patcher.start()
    mock.contacts = contacts
    request.addfinalizer(patcher.stop)
    return mock


@pytest.fixture(scope='function', autouse=True)
def geocode_timezone_mock(request):
    contacts = set()

    def geocode(service, contact):
        contacts.add(contact)

    patcher = patch('easybiodata.contacts.ContactService.geocode_timezone', geocode)
    mock = patcher.start()
    mock.contacts = contacts
    request.addfinalizer(patcher.stop)
    return mock


@pytest.fixture(scope='function')
def random_user(test_client):
    random_user = random_user_on_team()
    login_as_user(test_client, random_user, success_status=200, use_username=random.random() < 0.5)
    return random_user


@pytest.fixture(scope='function', autouse=True)
def upload_s3(request):
    def return_key(bucket_name, data, mimetype, prefix, suffix):
        from easybiodata.utils.s3_upload import _s3_key_for_data

        return _s3_key_for_data(data, prefix, suffix)

    patcher = patch('easybiodata.files.upload_s3', side_effect=return_key)
    mock = patcher.start()
    request.addfinalizer(patcher.stop)
    return mock


@pytest.fixture(scope='function', autouse=True)
def upload_with_boto(request):
    def return_key(data, prefix, sent_file):
        from easybiodata.utils.s3_upload import _s3_key_for_data
        from flask_login import current_user
        from easybiodata.services import images

        return images.create(creator=current_user,
                             bucket_name='easybiodata-file-uploads',
                             size_bytes=len(data),
                             key=_s3_key_for_data(data, prefix, sent_file.filename))

    patcher = patch('easybiodata.images.upload_with_boto', side_effect=return_key)
    mock = patcher.start()
    request.addfinalizer(patcher.stop)
    return mock
