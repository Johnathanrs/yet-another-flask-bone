import itertools
import random
from operator import itemgetter

import pytest

from easybiodata.contacts import Contact
from easybiodata.contacts.v1.schemas import ContactSchema
from easybiodata.services import contacts
from easybiodata.tests.functional import fake
from easybiodata.tests.utils.helpers import fake_id, nullable_field_names
from easybiodata.tests.utils.jsonschema import create_object_json_schema, id_string
from easybiodata.tests.utils.request_helpers import post_json, validate_response, put_json
from easybiodata.utils.helpers import get_value


def _company_for_user(user):
    return Contact.query.filter(Contact.team == user.team).first()


def _contact_for_user(user):
    return Contact.query.filter(Contact.team == user.team,
                                Contact.user_data == None).first()


def test_create_company(test_client, random_user, geocode_address_mock, geocode_timezone_mock):
    contact_request = _fake_company_request()
    rv = post_json(test_client, '/v1/contacts', contact_request)
    validate_response(rv, success_status=200, success_schema=create_object_json_schema({
        'id': id_string(),
    }))

    created_contact = contacts.get(rv.json['id'])
    assert created_contact is not None
    _validate_request_against_contact(contact_request, created_contact)
    _validate_contact_modified(created_contact, geocode_address_mock, geocode_timezone_mock)


@pytest.mark.parametrize('empty_list_field', [None])
def test_update_company(test_client, random_user, geocode_address_mock, geocode_timezone_mock,
                        empty_list_field):
    target_contact = _company_for_user(random_user)

    contact_request = _fake_company_request()
    if empty_list_field is not None:
        contact_request[empty_list_field] = []

    rv = put_json(test_client, '/v1/contacts/{}'.format(target_contact.id), contact_request)
    validate_response(rv, success_status=200, success_schema=create_object_json_schema({
        'id': id_string(),
    }))
    _validate_request_against_contact(contact_request, target_contact)
    _validate_contact_modified(target_contact, geocode_address_mock, geocode_timezone_mock)


def test_create_contact(test_client, random_user, geocode_address_mock, geocode_timezone_mock):
    parent_company = _company_for_user(random_user)

    contact_request = _fake_contact_request(parent_company.id)

    rv = post_json(test_client, '/v1/contacts', contact_request)
    validate_response(rv, success_status=200, success_schema=create_object_json_schema({
        'id': id_string(),
    }))

    created_contact = contacts.get(rv.json['id'])
    assert created_contact is not None
    _validate_request_against_contact(contact_request, created_contact)
    _validate_contact_modified(created_contact, geocode_address_mock, geocode_timezone_mock)


def test_update_contact(test_client, random_user, geocode_address_mock, geocode_timezone_mock):
    target_contact = _contact_for_user(random_user)

    contact_request = _fake_contact_request(target_contact.parent_company_id)

    rv = put_json(test_client, '/v1/contacts/{}'.format(target_contact.id), contact_request)
    validate_response(rv, success_status=200, success_schema=create_object_json_schema({
        'id': id_string(),
    }))
    _validate_request_against_contact(contact_request, target_contact)
    _validate_contact_modified(target_contact, geocode_address_mock, geocode_timezone_mock,
                               expect_geocode=False)


def test_create_contact_invalid_type(test_client, random_user, geocode_address_mock, geocode_timezone_mock):
    contact_request = _fake_company_request()
    contact_request['type'] = 'INVALID'

    rv = post_json(test_client, '/v1/contacts', contact_request)
    validate_response(rv, failure_status=400, failure_string='Not a valid choice.')
    _validate_contact_not_modified(geocode_address_mock, geocode_timezone_mock)


def test_create_contact_nonexistant_company(test_client, random_user, geocode_address_mock, geocode_timezone_mock):
    invalid_id = fake_id()
    contact_request = _fake_contact_request(invalid_id)

    rv = post_json(test_client, '/v1/contacts', contact_request)
    validate_response(rv, failure_status=400, failure_string='companyId {} not found'.format(invalid_id))
    _validate_contact_not_modified(geocode_address_mock, geocode_timezone_mock)


@pytest.mark.parametrize('bad_field', ['addressLine1',
                                       'addressLine2',
                                       'city',
                                       'region',
                                       'postalCode',
                                       'country'])
def test_create_contact_with_fields_that_should_be_empty(test_client, random_user, geocode_address_mock, geocode_timezone_mock,
                                                         bad_field):
    company = _company_for_user(random_user)
    request = _fake_contact_request(company.id)

    request[bad_field] = 'INVALID'

    rv = post_json(test_client, '/v1/contacts', request)
    validate_response(rv, failure_status=400, failure_string='must be')
    _validate_contact_not_modified(geocode_address_mock, geocode_timezone_mock)


@pytest.mark.parametrize('bad_field', ['addressLine1',
                                       'addressLine2',
                                       'city',
                                       'region',
                                       'postalCode',
                                       'country'])
def test_update_contact_with_fields_that_should_be_empty(test_client, random_user, geocode_address_mock, geocode_timezone_mock,
                                                         bad_field):
    company = _company_for_user(random_user)
    request = _fake_contact_request(company.id)

    request[bad_field] = 'INVALID'

    target_contact = _contact_for_user(random_user)

    rv = put_json(test_client, '/v1/contacts/{}'.format(target_contact.id), request)
    validate_response(rv, failure_status=400, failure_string='must be')
    _validate_contact_not_modified(geocode_address_mock, geocode_timezone_mock)


def test_create_company_with_company_id(test_client, random_user, geocode_address_mock, geocode_timezone_mock):
    request = _fake_company_request()
    request['companyId'] = fake_id()

    rv = post_json(test_client, '/v1/contacts', request)
    validate_response(rv, failure_status=400)
    _validate_contact_not_modified(geocode_address_mock, geocode_timezone_mock)


def test_update_company_with_company_id(test_client, random_user, geocode_address_mock, geocode_timezone_mock):
    target_contact = _company_for_user(random_user)
    request = _fake_company_request()
    request['companyId'] = fake_id()

    rv = put_json(test_client, '/v1/contacts/{}'.format(target_contact.id), request)
    validate_response(rv, failure_status=400)
    _validate_contact_not_modified(geocode_address_mock, geocode_timezone_mock)


# def test_change_contact_to_company(test_client, random_user, geocode_address_mock,
#                                    geocode_timezone_mock):
#     contact = _contact_for_user(random_user)
#     company_request = _fake_company_request()
#     company_request['type'] = 'Company'

#     rv = put_json(test_client, '/v1/contacts/{}'.format(contact.id), company_request)
#     validate_response(rv, failure_status=400, failure_string='is not a Company')
#     _validate_contact_not_modified(geocode_address_mock, geocode_timezone_mock)


# def test_change_company_to_contact(test_client, random_user, geocode_address_mock,
#                                    geocode_timezone_mock):
#     company = _company_for_user(random_user)
#     contact_request = _fake_contact_request(company.id)
#     contact_request['type'] = 'Contact'

#     rv = put_json(test_client, '/v1/contacts/{}'.format(company.id), contact_request)
#     validate_response(rv, failure_status=400, failure_string='is not a Contact')
#     _validate_contact_not_modified(geocode_address_mock, geocode_timezone_mock)


def test_update_nonexistant_contact(test_client, random_user, geocode_address_mock,
                                    geocode_timezone_mock):
    contact_request = _fake_contact_request(fake_id())

    rv = put_json(test_client, '/v1/contacts/{}'.format(fake_id()), contact_request)
    validate_response(rv, failure_status=404)
    _validate_contact_not_modified(geocode_address_mock, geocode_timezone_mock)


def test_create_contact_duplicate_email(test_client, random_user, geocode_address_mock, geocode_timezone_mock):
    other_contact = _contact_for_user(random_user)

    contact_request = _fake_contact_request(other_contact.parent_company_id)
    contact_request['email'] = other_contact.email

    rv = post_json(test_client, '/v1/contacts', contact_request)
    validate_response(rv, success_status=200, success_schema=create_object_json_schema({
        'id': id_string(),
    }))

    created_contact = contacts.get(rv.json['id'])
    assert created_contact is not None
    _validate_request_against_contact(contact_request, created_contact)
    _validate_contact_modified(created_contact, geocode_address_mock, geocode_timezone_mock)


def test_update_contact_duplicate_email(test_client, random_user, geocode_address_mock,
                                        geocode_timezone_mock):
    target_contact = _contact_for_user(random_user)

    other_contact = Contact.query.filter(Contact.team == random_user.team,
                                         Contact.user_data == None,
                                         Contact.id != target_contact.id).first()

    contact_request = _fake_contact_request(target_contact.parent_company_id)
    contact_request['email'] = other_contact.email

    rv = put_json(test_client, '/v1/contacts/{}'.format(target_contact.id), contact_request)
    validate_response(rv, success_status=200, success_schema=create_object_json_schema({
        'id': id_string(),
    }))
    _validate_request_against_contact(contact_request, target_contact)
    _validate_contact_modified(target_contact, geocode_address_mock, geocode_timezone_mock,
                               expect_geocode=False)


def _validate_request_against_contact(request, contact_model):
    synthesized = ContactSchema(strict=True,
                                exclude=('id', 'latitude', 'longitude', 'googlePlaceId', 'timezone', 'companyId')).dump(contact_model).data

    assert get_value('parent_company.id', contact_model) == request.pop('companyId')

####PAY ATTENTION HERE
    # assert synthesized == request


def _fake_contact_request(company_id):
    r = _fake_company_request()
    r['type'] = 'Contact'
    r['companyId'] = company_id
    r['addressLine1'] = None
    r['addressLine2'] = None
    r['city'] = None
    r['region'] = None
    r['postalCode'] = None
    r['country'] = None
    return r


def _fake_company_request():
    return {'name'        : fake.name(),
            'type'        : 'Company',
            'companyId'   : None,
            'phone'       : fake.phone_number(),
            'email'       : fake.email(),
            'website'     : fake.url(),
            'addressLine1': fake.street_address(),
            'addressLine2': fake.street_address(),
            'city'        : fake.city(),
            'region'      : fake.state(),
            'postalCode'  : fake.postcode(),
            'country'     : fake.random_element(['USA', 'CAN']),
            'notes'       : fake.sentence()}


@pytest.mark.parametrize('missing_field', _fake_contact_request(None).keys())
def test_create_contact_missing_fields(test_client, random_user, geocode_address_mock,
                                       geocode_timezone_mock, missing_field):
    contact_request = _fake_contact_request(_company_for_user(random_user).id)
    del contact_request[missing_field]

    rv = post_json(test_client, '/v1/contacts', contact_request)
    validate_response(rv, failure_status=400, failure_string=missing_field)
    _validate_contact_not_modified(geocode_address_mock, geocode_timezone_mock)


@pytest.mark.parametrize('missing_field', _fake_contact_request(None).keys())
def test_update_contact_missing_fields(test_client, random_user, geocode_address_mock,
                                       geocode_timezone_mock, missing_field):
    target_contact = _contact_for_user(random_user)
    contact_request = _fake_contact_request(target_contact.parent_company_id)
    del contact_request[missing_field]

    rv = put_json(test_client, '/v1/contacts/{}'.format(target_contact.id), contact_request)
    validate_response(rv, failure_status=400, failure_string=missing_field)
    _validate_contact_not_modified(geocode_address_mock, geocode_timezone_mock)


@pytest.mark.parametrize('null_field', nullable_field_names('easybiodata.contacts.v1.schemas', 'ContactSchema'))
def test_create_contact_null_fields(test_client, random_user, geocode_address_mock, geocode_timezone_mock,
                                    null_field):
    contact_request = _fake_contact_request(_company_for_user(random_user).id)

    contact_request[null_field] = None

    rv = post_json(test_client, '/v1/contacts', contact_request)
    validate_response(rv, success_status=200, success_schema=create_object_json_schema({
        'id': id_string(),
    }))

    created_contact = contacts.get(rv.json['id'])
    _validate_request_against_contact(contact_request, created_contact)
    _validate_contact_modified(created_contact, geocode_address_mock, geocode_timezone_mock)


@pytest.mark.parametrize('null_field', nullable_field_names('easybiodata.contacts.v1.schemas', 'ContactSchema'))
def test_update_contact_null_fields(test_client, random_user, geocode_address_mock, geocode_timezone_mock,
                                    null_field):
    target_contact = _contact_for_user(random_user)
    contact_request = _fake_contact_request(target_contact.parent_company_id)
    contact_request[null_field] = None

    rv = put_json(test_client, '/v1/contacts/{}'.format(target_contact.id), contact_request)
    validate_response(rv, success_status=200, success_schema=create_object_json_schema({
        'id': id_string(),
    }))
    _validate_request_against_contact(contact_request, target_contact)
    _validate_contact_modified(target_contact, geocode_address_mock, geocode_timezone_mock,
                               expect_geocode=False)


@pytest.mark.parametrize('empty_field', _fake_contact_request(None).keys())
def test_create_contact_empty_field(test_client, random_user, empty_field):
    contact_request = _fake_contact_request(_company_for_user(random_user).id)
    contact_request[empty_field] = ''

    rv = post_json(test_client, '/v1/contacts', contact_request)
    validate_response(rv, failure_status=400, failure_string=empty_field)


@pytest.mark.parametrize('empty_field', _fake_contact_request(None).keys())
def test_update_contact_empty_field(test_client, random_user, geocode_address_mock, geocode_timezone_mock,
                                    empty_field):
    target_contact = _contact_for_user(random_user)
    contact_request = _fake_contact_request(target_contact.parent_company_id)
    contact_request[empty_field] = ''

    rv = put_json(test_client, '/v1/contacts/{}'.format(target_contact.id), contact_request)
    validate_response(rv, failure_status=400, failure_string=empty_field)
    _validate_contact_not_modified(geocode_address_mock, geocode_timezone_mock)



@pytest.mark.parametrize('is_company', [True, False])
def test_update_contact_associated_with_load(test_client, random_user, geocode_address_mock,
                                             geocode_timezone_mock, is_company):
    query = Contact.query.filter(Contact.team == random_user.team,
                                 Contact.user_data == None)
    target_contact = query.first()

    if is_company:
        contact_request = _fake_company_request()
    else:
        contact_request = _fake_contact_request(target_contact.parent_company_id)

    rv = put_json(test_client, '/v1/contacts/{}'.format(target_contact.id), contact_request)
    validate_response(rv, success_status=200, success_schema=create_object_json_schema({
        'id': id_string(),
    }))
    _validate_request_against_contact(contact_request, target_contact)
    _validate_contact_modified(target_contact, geocode_address_mock, geocode_timezone_mock,
                               expect_geocode=False)


@pytest.mark.parametrize('updated_field', ['addressLine1',
                                           'addressLine2',
                                           'city',
                                           'region',
                                           'postalCode',
                                           'country'])
def test_update_company_single_address_field(test_client, random_user, geocode_address_mock,
                                             geocode_timezone_mock, updated_field):
    target_contact = _company_for_user(random_user)

    contact_request = _fake_company_request()
    contact_request['addressLine1'] = target_contact.address_line1
    contact_request['addressLine2'] = target_contact.address_line2
    contact_request['city'] = target_contact.city
    contact_request['region'] = target_contact.region
    contact_request['postalCode'] = target_contact.postal_code
    contact_request['country'] = target_contact.country
    contact_request[updated_field] = 'change'

    rv = put_json(test_client, '/v1/contacts/{}'.format(target_contact.id), contact_request)
    validate_response(rv, success_status=200, success_schema=create_object_json_schema({
        'id': id_string(),
    }))
    _validate_request_against_contact(contact_request, target_contact)
    _validate_contact_modified(target_contact, geocode_address_mock, geocode_timezone_mock)


def test_update_company_except_address(test_client, random_user, geocode_address_mock,
                                       geocode_timezone_mock):
    target_contact = _company_for_user(random_user)

    contact_request = _fake_company_request()
    contact_request['addressLine1'] = target_contact.address_line1
    contact_request['addressLine2'] = target_contact.address_line2
    contact_request['city'] = target_contact.city
    contact_request['region'] = target_contact.region
    contact_request['postalCode'] = target_contact.postal_code
    contact_request['country'] = target_contact.country

    rv = put_json(test_client, '/v1/contacts/{}'.format(target_contact.id), contact_request)
    validate_response(rv, success_status=200, success_schema=create_object_json_schema({
        'id': id_string(),
    }))
    _validate_request_against_contact(contact_request, target_contact)
    _validate_contact_modified(target_contact, geocode_address_mock, geocode_timezone_mock,
                               expect_geocode=False)


def _validate_contact_modified(contact, geocode_address_mock, geocode_timezone_mock, expect_geocode=True):
    def _contacts_associated_with_contact(contact):
        return itertools.chain([contact],
                               contact.company_contacts)

    assert contact is not None

    all_contacts = _contacts_associated_with_contact(contact)

    if expect_geocode:
        assert contact in geocode_address_mock.contacts
        assert contact in geocode_timezone_mock.contacts


def _validate_contact_not_modified(geocode_address_mock, geocode_timezone_mock):
    assert len(geocode_address_mock.contacts) == 0
    assert len(geocode_timezone_mock.contacts) == 0
