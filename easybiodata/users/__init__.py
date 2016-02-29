from easybiodata.core import Service
from easybiodata.users.models import UserData


class UserDataService(Service):
    __model__ = UserData
