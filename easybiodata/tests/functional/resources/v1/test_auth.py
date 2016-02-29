import pytest

from easybiodata.contacts import Contact
from easybiodata.tests.utils.jsonschema import create_object_json_schema, string_with_enum, string_with_length, \
    nullable, id_string
from easybiodata.tests.utils.request_helpers import post_json, validate_response, login_as_user, \
    post_data

from itsdangerous import URLSafeTimedSerializer
import unittest
from sqlalchemy.sql import func
from flask import current_app
import random


@pytest.fixture(scope='function')
def random_user_logged_out(test_client):
    random_user_logged_out = random.choice(Contact.query.filter(Contact.user_data != None).all())
    return random_user_logged_out


def test_login_username(test_client, random_user):
    rv = post_json(test_client, '/v1/auth/login', _login_request_json('asdfasdfasdf', random_user.user_data.username))
    _validate_login_or_refresh_response(random_user, rv)


def test_login_teammates(test_client, random_user):
    rv = post_json(test_client, '/v1/auth/login', _login_request_json('asdfasdfasdf', random_user.user_data.username))
    teammates = rv.json['teammates']
    teammate_models = Contact.query.filter(Contact.team_id == random_user.team_id,
                                           Contact.user_data != None).all()
    assert [{'id'      : u.id,
             'username': u.user_data.username} for u in teammate_models] == teammates


def test_login_nonexistant(test_client):
    rv = post_json(test_client, '/v1/auth/login', _login_request_json('asdfasdfasdf', 'invalid_usernam'))
    validate_response(rv, failure_status=401)


def test_login_invalid_password(test_client, random_user):
    rv = post_json(test_client, '/v1/auth/login',
                   _login_request_json('asdfasdfasdf123', random_user.user_data.username))
    validate_response(rv, failure_status=401)


def test_logout(test_client, random_user):
    login_as_user(test_client, random_user, success_status=200)

    rv = test_client.post('/v1/auth/refresh')
    validate_response(rv, success_status=200)

    rv = post_data(test_client, '/v1/auth/logout', data=None)
    validate_response(rv, success_status=200)

    rv = test_client.post('/v1/auth/refresh')
    validate_response(rv, failure_status=401)


def test_change_password_logs_you_out(test_client, random_user):
    from easybiodata.core import db

    login_as_user(test_client, random_user, success_status=200)

    test_client.cookie_jar.clear_session_cookies()

    random_user.user_data.password = 'asdfasdfasdf'
    db.session.add(random_user)
    db.session.commit()

    rv = test_client.post('/v1/auth/refresh')
    validate_response(rv, failure_status=401)


def test_invalid_remember_cookie(test_client, random_user):
    login_as_user(test_client, random_user, success_status=200)

    rv = test_client.post('/v1/auth/refresh')
    validate_response(rv, success_status=200)
    test_client.cookie_jar.clear_session_cookies()

    rv = test_client.post('/v1/auth/refresh')
    validate_response(rv, success_status=200)

    test_client.set_cookie('localhost', 'remember_token', 'asdf')
    test_client.cookie_jar.clear_session_cookies()

    rv = test_client.post('/v1/auth/refresh')
    validate_response(rv, failure_status=401)


def test_auth_refresh(test_client, random_user):
    rv = post_json(test_client, '/v1/auth/login', _login_request_json('asdfasdfasdf', random_user.user_data.username))
    _validate_login_or_refresh_response(random_user, rv)
    rv = test_client.post('/v1/auth/refresh')
    _validate_login_or_refresh_response(random_user, rv)


def test_auth_refresh_logged_out(test_client):
    rv = test_client.post('/v1/auth/refresh')
    validate_response(rv, failure_status=401)


def _validate_login_or_refresh_response(user, rv):
    user_schema = create_object_json_schema({'id'       : string_with_enum([user.id]),
                                             'teamId'   : nullable(string_with_enum([user.team_id])),
                                             'username' : string_with_enum([user.user_data.username]),
                                             'name'     : string_with_enum([user.name]),
                                             'email'    : string_with_enum([user.email]),
                                             'settings' : {'type': 'object'}})
    teammate_schema = {'type'    : 'array',
                       'minItems': 1,
                       'items'   : create_object_json_schema({'id'      : id_string(),
                                                              'username': string_with_length(1,
                                                                                             20)})}
    response_schema = create_object_json_schema({'user'                  : user_schema,
                                                 'teammates'             : teammate_schema})
    validate_response(rv, 200, response_schema)



def _create_user_json(password, username, email):
    return {'username' : username,
            'email'    : email,
            'password' : password}


def _login_request_json(password, username=None, email=None):
    assert (username is None) ^ (email is None)
    return {'usernameOrEmail': username if username is not None else email,
            'password'       : password}


@pytest.mark.parametrize('field', _login_request_json('asdfasdfasdf', 'joe@j.zz').keys())
def test_login_missing_fields(test_client, field):
    request = _login_request_json('asdfasdfasdf', 'john')
    del request[field]
    rv = post_json(test_client, '/v1/auth/login', request)
    validate_response(rv, failure_status=400, failure_string=field)


@pytest.mark.parametrize('field', _login_request_json('asdfasdfasdf', 'joe@j.zz').keys())
def test_login_null_fields(test_client, field):
    request = _login_request_json('asdfasdfasdf', 'john')
    request[field] = None
    rv = post_json(test_client, '/v1/auth/login', request)
    validate_response(rv, failure_status=400, failure_string=field)


@pytest.mark.parametrize('field', _login_request_json('asdfasdfasdf', 'joe@j.zz').keys())
def test_login_zero_length_fields(test_client, field):
    request = _login_request_json('asdfasdfasdf', 'john')
    request[field] = ''
    rv = post_json(test_client, '/v1/auth/login', request)
    validate_response(rv, failure_status=401,
                      failure_string='The server could not verify that you are authorized to access the URL requested')
