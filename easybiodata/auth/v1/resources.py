from flask import g, current_app
from flask.ext.login import logout_user, login_required, current_user
from werkzeug.exceptions import Unauthorized, BadRequest
from easybiodata.auth.v1.schemas import LoginSchema, LoginResponseSchema, ChangeEmailRequestSchema, ChangeEmailSchema
from easybiodata.contacts import Contact
from easybiodata.services import user_data, contacts
from easybiodata.utils.decorators import with_request_schema, with_response_schema
from flask.ext.restful import Resource

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from easybiodata.contacts import Contact
import requests

def _handle_login_or_refresh(user):
    contacts.touch_and_login_user(user, True)
    return {'user'          : user}


class Login(Resource):
    @with_request_schema(LoginSchema())
    @with_response_schema(LoginResponseSchema(strict=True))
    def post(self):
        username_or_email = g.deserialized['usernameOrEmail']

        user = None
        if '@' in username_or_email:
            user = Contact.query.filter(Contact.email == username_or_email,
                                        Contact.user_data != None).one_or_none()
            current_app.logger.info('No user found with email {}'.format(username_or_email))
        else:
            data = user_data.one_or_none(username=username_or_email)
            if data is not None:
                user = data.contact
            else:
                current_app.logger.info('No user found with username {}'.format(username_or_email))

        if user is not None:
            if user.verify_password(g.deserialized['password']):
                return _handle_login_or_refresh(user)
            else:
                current_app.logger.info('Password did not match for user {}'.format(user.id))

        raise Unauthorized()


class Logout(Resource):
    def post(self):
        logout_user()
        return {'success': True}


class Refresh(Resource):
    method_decorators = [login_required]

    @with_response_schema(LoginResponseSchema(strict=True))
    def post(self):
        return _handle_login_or_refresh(current_user._get_current_object())


class ChangeEmailRequest(Resource):
    method_decorators = [login_required]

    @with_request_schema(ChangeEmailRequestSchema())
    def post(self):
        email = g.deserialized['email']
        changeEmail = g.deserialized['changeEmail']
        user_check = Contact.query.filter(Contact.email == changeEmail,
                                        Contact.user_data != None).one_or_none()
        if user_check:
            raise BadRequest('User Account Already Associated With This Email')

        if current_user.verify_password(g.deserialized['password']):
            a = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            emailToken = a.dumps(changeEmail)

            return {"success":True}
        else:
            return BadRequest("Incorrect Password")

class ChangeEmail(Resource):

    @with_request_schema(ChangeEmailSchema())
    def post(self):
        username = g.deserialized['username']
        token = g.deserialized['token']

        user = Contact.query.filter(Contact.user_data != None).all()

        for each in user:
            if each.user_data.username == username:
                user = each
                break

        if user:
            a = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            new_email = a.loads(token, max_age=86400)
            contacts.update(user,
                         email=new_email,
                         commit=True)

            return {'success':True}

        else:
            raise BadRequest("Token Failed")
