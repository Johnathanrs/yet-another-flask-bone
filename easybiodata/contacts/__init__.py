import datetime
import time

from flask import current_app
from flask.ext.login import login_user
import requests
from requests.exceptions import RequestException

from easybiodata.contacts.models import Contact
from easybiodata.core import Service
from easybiodata.errors import ExternalServiceError
from easybiodata.utils.helpers import request_remote_ip


class ContactService(Service):
    __model__ = Contact

    def geocode_address(self, contact):
        self._isinstance(contact)
        address_elements = filter(lambda o: o is not None, [getattr(contact, attr) for attr in ('address_line1',
                                                                                                'address_line2',
                                                                                                'city',
                                                                                                'region',
                                                                                                'postal_code',
                                                                                                'country')])
        address_string = ','.join(address_elements)
        current_app.logger.info('Geocoding [{}]'.format(address_string))

        try:
            r = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params={
                'key'    : current_app.config['GOOGLE_API_KEY'],
                'address': address_string
            })
        except RequestException as e:
            current_app.logger.exception(e)
            raise ExternalServiceError()

        results = r.json()['results']
        if r.status_code == 200:
            if len(results) > 0:
                result = results[0]
                geo = result['geometry']['location']
                lat, lng = geo['lat'], geo['lng']
                contact.google_place_id = result['place_id']
                contact.latitude, contact.longitude = lat, lng
        else:
            contact.google_place_id = None
            contact.latitude, contact.longitude = None, None
            current_app.logger.info('Address geocoding failed for [{}] [{}]'.format(address_string), r.status_code)

    def geocode_timezone(self, contact):
        self._isinstance(contact)

        location_string = '{},{}'.format(contact.latitude, contact.longitude)
        current_app.logger.info('Geocoding timezone for ({})'.format(location_string))

        try:
            r = requests.get('https://maps.googleapis.com/maps/api/timezone/json', params={
                'key'      : current_app.config['GOOGLE_API_KEY'],
                'location' : location_string,
                'timestamp': int(time.time())
            })
        except RequestException as e:
            current_app.logger.exception(e)
            raise ExternalServiceError()

        if r.status_code == 200:
            contact.timezone = r.json().get('timeZoneId')
        else:
            contact.timezone = None
            current_app.logger.info('Timezone geocoding failed for ({}) [{}]'.format(location_string, r.status_code))

    def touch_and_login_user(self, user, remember):
        self._isinstance(user)
        remote_addr = request_remote_ip()

        old_current_login, new_current_login = user.user_data.current_login_at, datetime.datetime.now(datetime.timezone.utc)
        old_current_ip, new_current_ip = user.user_data.current_login_ip, remote_addr

        user.user_data.last_login_at = old_current_login or new_current_login
        user.user_data.current_login_at = new_current_login
        user.user_data.last_login_ip = old_current_ip or new_current_ip
        user.user_data.current_login_ip = new_current_ip
        user.user_data.login_count += 1
        self.save(user)

        login_user(user, remember)
