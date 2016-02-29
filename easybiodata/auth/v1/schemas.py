from marshmallow import fields

from easybiodata.contacts.v1.schemas import UserSchema
from easybiodata.utils.schema import easybiodataSchema


class LoginSchema(easybiodataSchema):
    usernameOrEmail = fields.String(required=True)
    password = fields.String(required=True)


class LoginResponseSchema(easybiodataSchema):
    user = fields.Nested(UserSchema,
                         required=True,
                         only=('id', 'username', 'name', 'email', 'settings'))


class ChangeEmailRequestSchema(easybiodataSchema):
    email = fields.String(required=True)
    password = fields.String(required=True)
    changeEmail = fields.String(required=True)


class ChangeEmailSchema(easybiodataSchema):
    username = fields.String(required=True)
    token = fields.String(required=True)
