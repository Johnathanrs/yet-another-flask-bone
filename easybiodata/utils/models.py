import datetime
from sqlalchemy import DateTime, func

from easybiodata.core import db


def get_now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


class Auditable(object):
    created_at = db.Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = db.Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=get_now_utc, index=True)
    deleted_at = db.Column(DateTime(timezone=True), index=True)


class SimpleString(object):
    def __repr__(self):
        return '{}: id={}, addr={}'.format('{}.{}'.format(self.__module__, self.__class__.__name__),
                                           self.id,
                                           hex(id(self)))
