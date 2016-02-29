
def add_routes(api):
    _add_v1_routes(api)


def _add_v1_routes(api):
    from easybiodata.users.v1.resources import UserSettings, CreateUser
    from easybiodata.contacts.v1.resources import Contact, Contacts
    from easybiodata.infrastructure.resources import Ping
    from easybiodata.auth.v1.resources import Login, Logout, Refresh, ChangeEmailRequest, ChangeEmail
    from easybiodata.images.v1.resources import Images, Image, ImageUpload


    api.add_resource(Ping, '/ping')

    api.add_resource(Contacts, '/v1/contacts')
    api.add_resource(Contact, '/v1/contacts/<string:id>')

    api.add_resource(Login, '/v1/auth/login')
    api.add_resource(Logout, '/v1/auth/logout')
    api.add_resource(Refresh, '/v1/auth/refresh')

    api.add_resource(ChangeEmailRequest, '/v1/auth/change_email_request')
    api.add_resource(ChangeEmail, '/v1/auth/change_email')

    api.add_resource(UserSettings, '/v1/me/settings')
    api.add_resource(CreateUser, '/v1/create_user')
    
    api.add_resource(Images, '/v1/images')
    api.add_resource(ImageUpload, '/v1/images/files')
    api.add_resource(Image, '/v1/image/<string:image_id>')
