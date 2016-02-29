from easybiodata.contacts import Contact
from easybiodata.services import teams, contacts, images
from easybiodata.tests.factories.models.contacts import ContactFactory
from easybiodata.tests.factories.models.users import UserDataFactory, TeamFactory
from easybiodata.tests.factories.models.images import ImageFactory



def create_test_data():
    _create_demo_data()
    _create_test_users()
    _create_test_contacts()
    _create_unassociated_images()



def _create_demo_data():
    team = TeamFactory.build(name='easybiodata',
                             email='easybiodata@easybiodata.com')
    user = ContactFactory.build(team=team,
                                name='Rob Kelly',
                                email='rob@easybiodata.com',
                                user_data=UserDataFactory.build(username='rob',
                                                                password='asdfasdfasdf'))
    contacts.save(user)


def _create_test_users():
    generated_teams = TeamFactory.build_batch(3)
    for team in generated_teams:
        generated_users = ContactFactory.build_batch(1,
                                                     team=team,
                                                     user_data=UserDataFactory.build())
        for u in generated_users:
            contacts.save(u)


def _create_test_contacts():
    users = Contact.query.filter(Contact.user_data != None).all()
    for user in users:
        generated_companies = [ContactFactory.build(creator=user) for i in range(3)]
        for company in generated_companies:
            generated_contacts = ContactFactory.build_batch(5,
                                                            parent_company=company,
                                                            creator=user)
            for contact in generated_contacts:
                contacts.save(contact)

def _create_unassociated_images():
    for user in Contact.query.filter(Contact.user_data != None).all():
        for i in ImageFactory.build_batch(5, creator=user):
            images.save(i)
