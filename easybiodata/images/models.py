from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import INTEGER, TEXT

from easybiodata.constants import easybiodata_MAX_NOTES_LENGTH
from easybiodata.core import db
from easybiodata.identifiers import generate_id
from easybiodata.utils.citext import CIText
from easybiodata.utils.helpers import text_length_range_check_constraint, nonnegative_number_check_constraint
from easybiodata.utils.models import SimpleString, Auditable


class Images(SimpleString, Auditable, db.Model):
    __tablename__ = 'profile_pictures'
    # __table_args__ = (text_length_range_check_constraint('notes', 1, easybiodata_MAX_NOTES_LENGTH),
    #                   text_length_range_check_constraint('bucket_name', 3, 63),
    #                   text_length_range_check_constraint('key', 1, 1024),
    #                   nonnegative_number_check_constraint('size_bytes'))

    id = db.Column(CIText, primary_key=True, default=generate_id)
    profile_id = db.Column(CIText, db.ForeignKey('profiles.id'), nullable=False)
    picture = db.Column(TEXT)
    created_at = db.Column(DateTime(timezone=False))
    updated_at = db.Column(DateTime(timezone=False))
