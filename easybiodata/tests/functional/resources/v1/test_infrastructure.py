from marshmallow import fields

from easybiodata.tests.utils.jsonschema import create_object_json_schema
from easybiodata.tests.utils.request_helpers import validate_response, get_json
from easybiodata.utils.decorators import with_response_schema
from easybiodata.utils.schema import easybiodataSchema


def test_ping(test_client):
    rv = get_json(test_client, '/ping')
    validate_response(rv, success_status=200, success_schema=create_object_json_schema({'pong': {'enum': [True]}}))


def test_404_error_json(test_client):
    rv = get_json(test_client, '/asdfasdfasdfasdf')
    validate_response(rv, failure_status=404, failure_string='The requested URL was not found on the server')


def test_set_status_code(flask_app):
    class TestSchema(easybiodataSchema):
        my_string = fields.String(required=True)

    @with_response_schema(TestSchema())
    def get():
        return {'my_string': 'hello'}, 201

    with flask_app.test_request_context():
        rv = get()
        validate_response(rv, success_status=201,
                          success_schema=create_object_json_schema({'my_string': {'enum': ['hello']}}))


def test_set_headers(flask_app):
    from marshmallow import fields
    from easybiodata.utils.decorators import with_response_schema

    class TestSchema(easybiodataSchema):
        my_string = fields.String(required=True)

    @with_response_schema(TestSchema())
    def get():
        return {'my_string': 'hello'}, 201, {'X-Test'  : 'test header',
                                             'X-Test-2': 'second test header'}

    with flask_app.test_request_context():
        rv = get()
        validate_response(rv, success_status=201,
                          success_schema=create_object_json_schema({'my_string': {'enum': ['hello']}}))
        assert rv.headers['X-Test'] == 'test header'
        assert rv.headers['X-Test-2'] == 'second test header'
