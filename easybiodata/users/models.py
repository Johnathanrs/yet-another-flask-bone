from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import TEXT, INET, INTEGER, JSONB, BOOLEAN
from werkzeug.security import generate_password_hash, check_password_hash

from easybiodata.core import db
from easybiodata.identifiers import generate_id
from easybiodata.utils.citext import CIText
from easybiodata.utils.helpers import text_length_range_check_constraint, \
    text_length_positive_check_constraint, nonnegative_number_check_constraint
from easybiodata.utils.models import SimpleString, Auditable


class UserData(db.Model):
    __tablename__ = 'profiles'
    # __table_args__ = (text_length_positive_check_constraint('password_hash'),
                      # nonnegative_number_check_constraint('login_count'))

    id = db.Column(CIText, primary_key=True, default=generate_id)
    owner_id = db.Column(INTEGER)
    relation_with_owner_id = db.Column(INTEGER)
    religion_id = db.Column(INTEGER)
    gothra = db.Column(CIText)
    caste = db.Column(CIText)
    birth_city = db.Column(CIText)
    height = db.Column(INTEGER)
    complexion = db.Column(CIText)
    description = db.Column(CIText)
    residence_country = db.Column(CIText)
    residence_city = db.Column(CIText)
    contact_email = db.Column(CIText)
    education_level_id = db.Column(INTEGER)
    created_at = db.Column(DateTime(timezone=False))
    updated_at = db.Column(DateTime(timezone=False))
    birth_datetime = db.Column(DateTime(timezone=False))
    template_id = db.Column(INTEGER)
    is_active = db.Column(BOOLEAN)
    gender = db.Column(CIText)
    first_name = db.Column(CIText)
    last_name = db.Column(CIText)
    birth_country = db.Column(CIText)
    residence_state = db.Column(CIText)
    pdf_generated_at = db.Column(DateTime(timezone=True))
    pdf_path = db.Column(CIText)
    matching_opt_in = db.Column(BOOLEAN)
    additional_information = db.Column(CIText)
    annual_income = db.Column(CIText)
    own_house = db.Column(CIText)
    own_car = db.Column(CIText)
    drink = db.Column(CIText)
    smoke = db.Column(CIText)
    blood_type = db.Column(CIText)
    diet = db.Column(CIText)
    family_values = db.Column(CIText)

    # _password_hash = db.Column('password_hash', TEXT, nullable=True)
    # last_login_at = db.Column(DateTime(timezone=True))
    # current_login_at = db.Column(DateTime(timezone=True))
    # last_login_ip = db.Column(INET)
    # current_login_ip = db.Column(INET)
    # login_count = db.Column(INTEGER, nullable=False, server_default='0')

    @property
    def password(self):
        raise AttributeError('Password is not readable')

    @password.setter
    def password(self, password):
        if len(password) < 5:
            raise AttributeError('Password must be at least {} characters long'.format(7))
        self._password_hash = generate_password_hash(password, method='pbkdf2:sha1:16000', salt_length=12)

    def verify_password(self, password):
        return check_password_hash(self._password_hash, password)

    def __repr__(self, *args, **kwargs):
        return '{}: addr={}'.format('{}.{}'.format(self.__module__, self.__class__.__name__),
                                                   hex(id(self)))
