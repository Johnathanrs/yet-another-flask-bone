import random

import factory

from easybiodata.users import UserData, Team


class TeamFactory(factory.Factory):
    class Meta:
        model = Team

    name = factory.Faker('company')


class UserDataFactory(factory.Factory):
    class Meta:
        model = UserData

    username = factory.Faker('lexify', text='????????')
    email = factory.Faker('email')
    password = 'asdfasdfasdf'
    settings = factory.LazyAttribute(lambda _: {} if random.random() < 0.5 else {'hello': 'world'})
