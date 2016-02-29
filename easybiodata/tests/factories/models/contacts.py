import random

import factory

from easybiodata.contacts import Contact
from easybiodata.tests.factories import fake
from easybiodata.tests.factories.models import ACCEPTABLE_TIMEZONES

from easybiodata.tests.factories.models.images import ImageFactory


class ContactFactory(factory.Factory):
    class Meta:
        model = Contact

    name = factory.Faker('name')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')
    website = factory.Faker('url')

    address_line1 = factory.LazyAttribute(lambda o: fake.street_address())
    address_line2 = factory.LazyAttribute(lambda o: fake.street_address())
    city = factory.LazyAttribute(lambda o: fake.city())
    region = factory.LazyAttribute(lambda o: fake.state())
    postal_code = factory.LazyAttribute(lambda o: fake.postcode())
    country = factory.LazyAttribute(lambda o: fake.country())

    google_place_id = factory.Faker('lexify', text='????????????????????')
    latitude = factory.LazyAttribute(lambda _: random.uniform(30.22, 48.86))
    longitude = factory.LazyAttribute(lambda _: random.uniform(-125, -67))
    timezone = factory.Faker('random_element', elements=ACCEPTABLE_TIMEZONES)

    notes = factory.Faker('text')

    user_data = None
    parent_company = None

    creator = None
    team = factory.LazyAttribute(lambda o: o.creator.team)
