import hashids
from sqlalchemy import text

from easybiodata.core import db

ID_ALPHABET = 'abcdefghjkmnpqrstuvwxyz123456789'

_hasher = hashids.Hashids(min_length=5,
                          salt='XiSeWVFlbqOMlEZrUnspFeTXCcnLBXID',
                          alphabet=ID_ALPHABET)


def generate_id():
    next_val = db.engine.scalar("SELECT nextval('id_sequence')")
    return _hasher.encode(next_val)
