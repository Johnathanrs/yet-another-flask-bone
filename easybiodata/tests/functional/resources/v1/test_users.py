import pytest

from easybiodata.tests.utils.jsonschema import id_string, create_object_json_schema
from easybiodata.tests.utils.request_helpers import get_json, put_json, validate_response, put_data


def test_get_user_settings(test_client, random_user):
    rv = get_json(test_client, '/v1/me/settings')
    validate_settings_response(random_user, rv)


@pytest.mark.parametrize('settings', [{},
                                      {'a': 'b'},
                                      {'a': {'b': 3}}])
def test_update_user_settings(test_client, random_user, settings):
    rv = put_json(test_client, '/v1/me/settings', settings)
    validate_response(rv, success_status=200, success_schema=create_object_json_schema({
        'id': id_string()
    }))


@pytest.mark.parametrize('settings', [[],
                                      'string',
                                      3,
                                      True])
def test_update_user_settings_not_dictionary(test_client, random_user, settings):
    rv = put_json(test_client, '/v1/me/settings', settings)
    validate_response(rv, failure_status=400)


@pytest.mark.parametrize('settings', ['{}',
                                      '[]',
                                      b'\xfa\x11\x95\x8f{\xcd\xe7\xed<\x0b'])
@pytest.mark.parametrize('content_type', ['text/plain',
                                          'x-www-form-urlencoded'])
def test_update_user_settings_not_json(test_client, random_user, settings, content_type):
    rv = put_data(test_client, '/v1/me/settings', settings, content_type=content_type)
    validate_response(rv, failure_status=400)


def validate_settings_response(user, rv):
    validate_response(rv, success_status=200)
    assert rv.json == user.user_data.settings
