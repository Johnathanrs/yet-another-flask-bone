from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import TEXT, INET, INTEGER, JSONB
from werkzeug.security import generate_password_hash, check_password_hash

from easybiodata.core import db
from easybiodata.identifiers import generate_id
from easybiodata.utils.citext import CIText
from easybiodata.utils.helpers import text_length_range_check_constraint, \
    text_length_positive_check_constraint, nonnegative_number_check_constraint
from easybiodata.utils.models import SimpleString, Auditable


class MatchingLog(db.Model):
    __tablename__ = 'matching_log'
    # __table_args__ = (text_length_range_check_constraint('username', 1, 100),
                      # nonnegative_number_check_constraint('login_count'))
    id = db.Column(CIText, primary_key=True, default=generate_id)
    male_user_id = db.Column(CIText, db.ForeignKey('profiles.id'), primary_key=True)
    female_user_id = db.Column(CIText, db.ForeignKey('profiles.id'), primary_key=True)
    match_sent = db.Column(DateTime(timezone=True))
    male_response = db.Column(CIText)
    female_response = db.Column(CIText)
