import datetime

from marshmallow import Schema, ValidationError
from marshmallow.fields import Field, String
import pytz


class easybiodataSchema(Schema):
    pass


class UNIXTimestamp(Field):
    def _serialize(self, value, attr, obj):
        if not isinstance(value, datetime.datetime):
            raise ValidationError('UNIXTimestamp field can only serialize datetime objects')
        if value.tzinfo is None:
            raise ValidationError('Attempt to serialize a naive datetime')
        return int(value.timestamp())

    def _deserialize(self, value, attr, data):
        try:
            timestamp = int(value)
        except (TypeError, ValueError):
            raise ValidationError('Could not convert {} to int'.format(value))
        return datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)


class UNIXString(String):
    def _deserialize(self, value, attr, data):
        s = super()._deserialize(value, attr, data)
        return '\n'.join(s.splitlines())
