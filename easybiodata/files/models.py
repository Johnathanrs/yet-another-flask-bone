from sqlalchemy.dialects.postgresql import INTEGER, TEXT

from easybiodata.constants import easybiodata_MAX_NOTES_LENGTH
from easybiodata.core import db
from easybiodata.identifiers import generate_id
from easybiodata.utils.citext import CIText
from easybiodata.utils.helpers import text_length_range_check_constraint, nonnegative_number_check_constraint
from easybiodata.utils.models import SimpleString, Auditable


class File(SimpleString, Auditable, db.Model):
    __tablename__ = 'files'
    __table_args__ = (text_length_range_check_constraint('notes', 1, easybiodata_MAX_NOTES_LENGTH),
                      text_length_range_check_constraint('bucket_name', 3, 63),
                      text_length_range_check_constraint('key', 1, 1024),
                      nonnegative_number_check_constraint('size_bytes'))

    id = db.Column(CIText, primary_key=True, default=generate_id)

    creator_id = db.Column(CIText, db.ForeignKey('contacts.id'), nullable=False)
    creator = db.relationship('Contact')

    notes = db.Column(TEXT)

    bucket_name = db.Column(TEXT, nullable=False)
    key = db.Column(TEXT, nullable=False)

    size_bytes = db.Column(INTEGER, nullable=False)
