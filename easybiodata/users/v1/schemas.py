from marshmallow import validate, fields, validates_schema, ValidationError
from marshmallow import Schema

from easybiodata.utils.schema import easybiodataSchema
from easybiodata.constants import easybiodata_USERNAME_REGEX


class CreateUserSchema(easybiodataSchema):
    username = fields.String(required=True,
                             validate=validate.Length(5, 20))
    email = fields.String(required=True,
                          validate=validate.Length(4, 100))
    password = fields.String(required=True,
                             validate=validate.Length(5, 20))
