import os

import mandrill
from geopy.geocoders import Nominatim

from easybiodata.services import user_data


def _get_location(user):
    gelocator = Nominatim()
    location = geolocator.geocode(user.residence_city + " " + user.residence_country)
    return location.longitude, location.latitude


def _get_distance(location1, location2):
    return sqrt((location1[0] - location2[0])**2 + (location1[1] - location2[1])**2)


def send_connection(recipient, match):
    mandrill_client = mandrill.Mandrill(os.environ['Mandrill_API_Key'])
    result = mandrill_client.messages.send(message=message,
                                           async=False,
                                           ip_pool='Main Pool',
                                           send_at='0000-11-11')


def get_matches(user):
    location = _get_location(user)
    if user.gender == 'male':
        matches = user_data.find(gender='female').all()
    else:
        matches = user_data.find(gender='male').all()
    matches.sort(key = lambda p: _get_distance(_get_location(p), location))
    if 
