import itertools

from flask import g
from flask.ext.login import login_required, current_user
from werkzeug.exceptions import NotFound, BadRequest

from easybiodata.contacts.v1.schemas import ContactSchema
from easybiodata.core import db
from easybiodata.services import contacts
from easybiodata.utils.decorators import with_request_schema, with_response_schema
from flask.ext.restful import Resource


def _validate_parent_company():
    company_id = g.deserialized.get('parent_company_id')
    if company_id is not None:
        company = contacts.first(id=company_id)
        if company is None:
            raise BadRequest('companyId {} not found'.format(company_id))


def _update_contact(contact):
    contact_type = g.deserialized.pop('type')
    _validate_parent_company()

    return contacts.update(contact, commit=False, **g.deserialized)


def _create_contact():
    comp_data = None
    _validate_parent_company()
    g.deserialized.pop('type')
    return contacts.new(creator=current_user, **g.deserialized)


class Contacts(Resource):
    method_decorators = [login_required]

    @with_request_schema(ContactSchema())
    @with_response_schema(ContactSchema(strict=True, only=('id',)))
    def post(self):
        with db.session.no_autoflush:
            contact = _create_contact()

            contacts.geocode_address(contact)
            contacts.geocode_timezone(contact)

            contacts.save(contact)

        return contact


def _needs_geocode(model):
    address_attrs = ('address_line1',
                     'address_line2',
                     'city',
                     'region',
                     'postal_code',
                     'country')

    for attr in address_attrs:
        if getattr(model, attr) != g.deserialized[attr]:
            return True
    return False


class Contact(Resource):
    method_decorators = [login_required]

    @with_request_schema(ContactSchema())
    @with_response_schema(ContactSchema(strict=True, only=('id',)))
    def put(self, id):
        contact = contacts.first(id=id)
        if contact is None:
            raise NotFound()

        with db.session.no_autoflush:
            needs_geocode = _needs_geocode(contact)

            contact = _update_contact(contact)
            if needs_geocode:
                contacts.geocode_address(contact)
                contacts.geocode_timezone(contact)

            contacts.save(contact)

        return contact
