from flask import json, Response
import jsonschema
from easybiodata.core import db

from easybiodata.tests.utils.jsonschema import create_object_json_schema, number_with_enum


def extract_json(rv):
    assert rv.content_type == 'application/json'
    rv.json = json.loads(str(rv.data, encoding='utf8'))


def post_data(test_client, path, data, **kwargs):
    rv = test_client.post(path, data=data, **kwargs)
    db.session.rollback()
    extract_json(rv)
    return rv


def post_json(test_client, path, data, **kwargs):
    rv = test_client.post(path, data=json.dumps(data), content_type='application/json', **kwargs)
    db.session.rollback()
    extract_json(rv)
    return rv


def get_json(test_client, path, **kwargs):
    rv = test_client.get(path, content_type='application/json', **kwargs)
    db.session.rollback()
    extract_json(rv)
    return rv


def put_json(test_client, path, data, **kwargs):
    rv = test_client.put(path, data=json.dumps(data), content_type='application/json', **kwargs)
    db.session.rollback()
    extract_json(rv)
    return rv


def put_data(test_client, path, data, **kwargs):
    rv = test_client.put(path, data=data, **kwargs)
    db.session.rollback()
    extract_json(rv)
    return rv


def delete(test_client, path, **kwargs):
    rv = test_client.delete(path, **kwargs)
    db.session.rollback()
    extract_json(rv)
    return rv


def assert_matches_json_schema(schema, rv):
    extract_json(rv)
    jsonschema.Draft4Validator.check_schema(schema)
    jsonschema.validate(rv.json, schema)


def validate_response(rv, success_status=None, success_schema=None, failure_status=None, failure_string=None):
    assert (success_status is None) ^ (failure_status is None)
    if failure_status is not None:
        assert failure_status >= 400
    if success_status is not None:
        assert 200 <= success_status <= 399
    assert isinstance(rv, Response)

    if success_status is not None:
        assert rv.status_code == success_status
        if success_schema is not None:
            assert_matches_json_schema(success_schema, rv)
    elif failure_status is not None:
        assert rv.status_code == failure_status
        schema = create_object_json_schema({'status' : number_with_enum([failure_status]),
                                            'message': {}},
                                           optional='status')
        assert_matches_json_schema(schema, rv)
        if failure_string is not None:
            assert failure_string in str(rv.data, encoding='utf8')


def login_as_user(test_client, user, use_username=True, success_status=None, failure_status=None):
    assert user is not None
    rv = post_json(test_client, '/v1/auth/login', {
        'usernameOrEmail': user.user_data.username if use_username else user.email,
        'password'       : 'asdfasdfasdf'
    })
    validate_response(rv, success_status, failure_status=failure_status)
    return rv


def logout(test_client):
    rv = get_json(test_client, '/auth/logout')
    validate_response(rv, 200)
    return rv
