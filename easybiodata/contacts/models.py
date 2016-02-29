from flask.ext.login import make_secure_token, UserMixin
from sqlalchemy import CheckConstraint, or_
from sqlalchemy.dialects.postgresql import ARRAY, TEXT, FLOAT
from sqlalchemy.orm import column_property
from werkzeug.security import safe_str_cmp

from easybiodata import login_manager
from easybiodata.core import db
from easybiodata.identifiers import generate_id
from easybiodata.utils.citext import CIText
from easybiodata.utils.helpers import text_length_range_check_constraint
from easybiodata.utils.models import Auditable, SimpleString


class Contact(db.Model, Auditable, UserMixin, SimpleString):
    __tablename__ = 'contacts'
    __table_args__ = (text_length_range_check_constraint('id', 1, 100),
                      text_length_range_check_constraint('name', 1, 100),
                      text_length_range_check_constraint('phone', 1, 100),
                      text_length_range_check_constraint('email', 1, 100),
                      text_length_range_check_constraint('website', 1, 100),
                      text_length_range_check_constraint('address_line1', 1, 100),
                      text_length_range_check_constraint('address_line2', 1, 100),
                      text_length_range_check_constraint('city', 1, 100),
                      text_length_range_check_constraint('region', 1, 100),
                      text_length_range_check_constraint('postal_code', 1, 100),
                      text_length_range_check_constraint('country', 1, 100),
                      text_length_range_check_constraint('notes', 1, 1000),
                      CheckConstraint(
                          '(latitude IS NULL AND longitude IS NULL) OR (latitude IS NOT NULL AND longitude IS NOT NULL)',
                          'lat_lon'),
                      CheckConstraint('(google_place_id IS NULL AND latitude is NULL) OR '
                                      '(google_place_id IS NOT NULL AND latitude is NOT NULL)',
                                      'place_id_coordinate'),
                      text_length_range_check_constraint('timezone', 1, 100))

    id = db.Column(CIText, primary_key=True, default=generate_id)

    creator_id = db.Column(CIText, db.ForeignKey('contacts.id'))
    creator = db.relationship('Contact', uselist=False, foreign_keys=[creator_id])

    name = db.Column(CIText)
    phone = db.Column(TEXT)
    email = db.Column(CIText)
    website = db.Column(TEXT)

    address_line1 = db.Column(TEXT)
    address_line2 = db.Column(TEXT)
    city = db.Column(TEXT)
    region = db.Column(TEXT)
    postal_code = db.Column(TEXT)
    country = db.Column(TEXT)

    google_place_id = db.Column(TEXT)

    latitude = db.Column(FLOAT)
    longitude = db.Column(FLOAT)
    timezone = db.Column(TEXT)

    notes = db.Column(TEXT)

    has_location = column_property(or_(address_line1.isnot(None),
                                       address_line2.isnot(None),
                                       city.isnot(None),
                                       region.isnot(None),
                                       postal_code.isnot(None),
                                       country.isnot(None)))

    parent_company_id = db.Column(CIText, db.ForeignKey('contacts.id'))
    parent_company = db.relationship('Contact',
                                     backref=db.backref('company_contacts', remote_side=[parent_company_id]),
                                     foreign_keys=[parent_company_id],
                                     remote_side=[id])

    def get_auth_token(self):
        token = '{}|{}'.format(self.id, make_secure_token(self.user_data._password_hash))
        return token

    def verify_password(self, password):
        if self.user_data is None:
            return False
        return self.user_data.verify_password(password)


@login_manager.user_loader
def load_user_from_id(user_id):
    return Contact.query.filter(Contact.id == user_id,
                                Contact.user_data != None).one_or_none()


@login_manager.token_loader
def load_user_from_token(token):
    try:
        user_id, pw_hash = token.rsplit('|', 1)
    except ValueError:
        return None
    contact = Contact.query.filter(Contact.id == user_id,
                                   Contact.user_data != None).one_or_none()
    if contact is not None and safe_str_cmp(pw_hash, make_secure_token(contact.user_data._password_hash)):
        return contact
    return None
