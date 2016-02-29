import pytest

from easybiodata.contacts import Contact
from easybiodata.tests.utils.jsonschema import create_object_json_schema, string_with_enum, string_with_length, \
    nullable, id_string
from easybiodata.tests.utils.request_helpers import post_json, validate_response, login_as_user, \
    post_data, put_data, put_json

from itsdangerous import URLSafeTimedSerializer
import unittest
from sqlalchemy.sql import func
from flask import current_app
import random
from easybiodata.tests.functional.resources.v1.common import input_file
from easybiodata.services import images, imagelikes, user_data


def _create_user_json(password, username, email):
    return {'username' : username,
            'email'    : email,
            'password' : password}


def _login_request_json(password, username=None, email=None):
    assert (username is None) ^ (email is None)
    return {'usernameOrEmail': username if username is not None else email,
            'password'       : password}


def test_register(test_client, upload_with_boto):
    username = 'newuser{}'.format(random.randint(100,1000))
    email = '{}@user.com'.format(username)
    rv = post_json(test_client, '/v1/create_user', _create_user_json('asdfasdfasdf', username, email))
    validate_response(rv, success_status=200)
    user_id=rv.json['id']
    rv = post_json(test_client, '/v1/auth/login', _login_request_json('asdfasdfasdf', username))
    validate_response(rv, success_status=200)

    with input_file('Lenna.jpg', mode='rb') as f:
        rv = put_data(test_client, '/v1/images/files', {'Lenna.jpg': (f, 'Lenna.jpg')})
    validate_response(rv, success_status=200)
    imageId1 = rv.json['imageId']

    with input_file('Lenna.jpg', mode='rb') as f:
        rv = put_data(test_client, '/v1/images/files', {'Lenna.jpg': (f, 'Lenna.jpg')})
    validate_response(rv, success_status=200)

    imageId2 = rv.json['imageId']
    my_image = images.get(imageId2)
    assert my_image

    from easybiodata.services import files
    assert rv.json['imageUrl'] == files.generate_url(my_image)
    assert upload_with_boto.call_count == 2
    (_, _, file), _ = upload_with_boto.call_args
    assert 'Lenna.jpg' == file.filename

    rv = put_json(test_client, '/v1/likes', {'imageId': imageId1})
    validate_response(rv, success_status=200)
    rv = put_json(test_client, '/v1/likes', {'imageId': imageId2})
    validate_response(rv, success_status=200)

    rv = put_json(test_client, '/v1/tags', {'imageId': imageId1, 'tags':['hot', 'fun', 'easy', 'weird']})
    validate_response(rv, success_status=200)

    image = images.get(imageId1)
    user = user_data.get(user_id)
    assert len(user.imagelikes) == 2

    rv = post_data(test_client, '/v1/auth/logout', data=None)
    validate_response(rv, success_status=200)

    with input_file('Lenna.jpg', mode='rb') as f:
        rv = put_data(test_client, '/v1/images/files', {'Lenna.jpg': (f, 'Lenna.jpg')})
    validate_response(rv, failure_status=401)

    #login second user and like picture twice
    username2 = '2user{}'.format(random.randint(100,1000))
    email2 = '{}@user.com'.format(username2)
    rv = post_json(test_client, '/v1/create_user', _create_user_json('asdfasdfasdf', username2, email2))
    validate_response(rv, success_status=200)
    rv = post_json(test_client, '/v1/auth/login', _login_request_json('asdfasdfasdf', username2))
    validate_response(rv, success_status=200)

    rv = put_json(test_client, '/v1/likes', {'imageId': imageId1})
    validate_response(rv, success_status=200)
    rv = put_json(test_client, '/v1/likes', {'imageId': imageId1})
    validate_response(rv, failure_status=400)
