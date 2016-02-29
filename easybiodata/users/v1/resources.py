from flask import request, g
from flask_login import current_user, login_required
from werkzeug.exceptions import BadRequest

from easybiodata.contacts.v1.schemas import UserSchema
from easybiodata.users.v1.schemas import CreateUserSchema
from easybiodata.services import user_data, contacts
from easybiodata.utils.decorators import with_json_request, with_response_schema, with_request_schema
from flask.ext.restful import Resource


class UserSettings(Resource):
    method_decorators = [login_required]

    @with_json_request()
    @with_response_schema(UserSchema(only=('id',)))
    def put(self):
        new_settings = request.get_json()
        if not isinstance(new_settings, dict):
            raise BadRequest('Settings must be a dictionary')

        user_data.update(current_user.user_data,
                         settings=new_settings,
                         commit=True)
        return current_user

    def get(self):
        return current_user.user_data.settings

class CreateUser(Resource):

    @with_request_schema(CreateUserSchema())
    @with_response_schema(UserSchema(only=('id',)))
    def post(self):

        print('fail')

        if user_data.find(email=g.deserialized['email']).first() is not None:
            print(user_data.find(email=g.deserialized['email']).first())
            raise BadRequest('Already user With that email')

        if user_data.find(username=g.deserialized['username']).first() is not None:
            raise BadRequest('Already user With that username')

        contact = contacts.create(email = g.deserialized['email'])
        user = user_data.create(contact_id=contact.id,
                                **g.deserialized)
        return contact
