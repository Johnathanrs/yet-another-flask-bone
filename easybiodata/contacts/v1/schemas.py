from marshmallow import validate, fields, validates_schema, ValidationError
from marshmallow import Schema

from easybiodata.utils.schema import easybiodataSchema
from easybiodata.constants import easybiodata_USERNAME_REGEX


class ContactSchemaBase(easybiodataSchema):
    public_fields = ('id',
                     'username',
                     'email',
                     'name',
                     'phone',
                     'email',
                     'website',
                     'addressLine1',
                     'addressLine2',
                     'city',
                     'region',
                     'postalCode',
                     'country')

    id = fields.String(dump_only=True)

    companyId = fields.String(required=True,
                              attribute='parent_company_id',
                              allow_none=True)

    name = fields.String(required=True,
                         validate=validate.Length(1, 100),
                         allow_none=True)
    phone = fields.String(required=True,
                          validate=validate.Length(1, 100),
                          allow_none=True)
    email = fields.Email(required=True,
                         validate=validate.Length(1, 100),
                         allow_none=True)
    website = fields.Url(required=True,
                         validate=validate.Length(1, 100),
                         allow_none=True)

    addressLine1 = fields.String(attribute='address_line1',
                                 required=True,
                                 validate=validate.Length(1, 100),
                                 allow_none=True)
    addressLine2 = fields.String(attribute='address_line2',
                                 required=True,
                                 validate=validate.Length(1, 100),
                                 allow_none=True)
    city = fields.String(required=True,
                         validate=validate.Length(1, 100),
                         allow_none=True)
    region = fields.String(required=True,
                           validate=validate.Length(1, 100),
                           allow_none=True)
    postalCode = fields.String(attribute='postal_code',
                               required=True,
                               validate=validate.Length(1, 100),
                               allow_none=True)
    country = fields.String(required=True,
                            validate=validate.Length(1, 100),
                            allow_none=True)

    googlePlaceId = fields.String(dump_only=True,
                                  required=True,
                                  attribute='google_place_id',
                                  allow_none=True)
    latitude = fields.Float(dump_only=True,
                            required=True,
                            validate=validate.Range(-90, 90),
                            allow_none=True)
    longitude = fields.Float(dump_only=True,
                             required=True,
                             validate=validate.Range(-180, 180),
                             allow_none=True)
    timezone = fields.String(dump_only=True,
                             required=True,
                             allow_none=True)

    notes = fields.String(required=True,
                          validate=validate.Length(1, 1000),
                          allow_none=True)


class ContactSchema(ContactSchemaBase):
    type = fields.String(required=True,
                         validate=validate.OneOf(['Contact', 'Company']))

    @validates_schema
    def validate_type(self, data):
        contact_type = data.get('type')
        company_id = data.get('parent_company_id')

        if contact_type == 'Contact':
            must_be_null = ['addressLine1',
                            'addressLine2',
                            'city',
                            'region',
                            'postalCode',
                            'country']

            for field_name in must_be_null:
                field = self.fields[field_name]
                attr = field.attribute if field.attribute is not None else field.name
                if data.get(attr) is not None:
                    raise ValidationError('{} must be null for Contacts'.format(field_name), [field_name])


    def get_attribute(self, attr, obj, default):
        inherited = {'address_line1',
                     'address_line2',
                     'city',
                     'region',
                     'postal_code',
                     'country',
                     'google_place_id',
                     'latitude',
                     'longitude',
                     'timezone',
                     'external_ids',
                     'has_location'}
        if obj.user_data is None and attr in inherited:
            attr = 'parent_company.' + attr
        return super().get_attribute(attr, obj, default)

    def make_type(self, obj):
        if obj.company_data is not None:
            return 'Company'
        if obj.user_data is not None:
            return 'User'
        return 'Contact'


class UserSchema(ContactSchemaBase):
    username = fields.String(attribute='user_data.username',
                             required=True,
                             validate=validate.Regexp(easybiodata_USERNAME_REGEX))

    settings = fields.Dict(attribute='user_data.settings')
