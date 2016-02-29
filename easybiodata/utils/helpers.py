import ipaddress

from flask import request
from sqlalchemy import CheckConstraint


def text_length_range_check_constraint(column_name, min_length, max_length):
    assert min_length < max_length
    return CheckConstraint('LENGTH({}) BETWEEN {} AND {}'.format(column_name, min_length, max_length),
                           '{}_length'.format(column_name))


def text_length_positive_check_constraint(column_name):
    return CheckConstraint('LENGTH({}) > 0'.format(column_name), '{}_length_positive'.format(column_name))


def nonnegative_number_check_constraint(column_name):
    return CheckConstraint('{} >= 0'.format(column_name), '{}_nonnegative'.format(column_name))


def request_remote_ip():
    if 'X-Forwarded-For' not in request.headers:
        return request.remote_addr
    forwarded_for = request.headers.getlist('X-Forwarded-For')[0]
    if len(forwarded_for) > 0:
        ip_string = forwarded_for.split(',')[0]
        try:
            ipaddress.ip_address(ip_string)
        except ValueError:
            pass
        else:
            return ip_string
    return None


# get_value borrowed from marshmallow.utils
def get_value(key, obj, default=None):
    if type(key) == int:
        return _get_value_for_key(key, obj, default)
    return _get_value_for_keys(key.split('.'), obj, default)


def _get_value_for_keys(keys, obj, default):
    if len(keys) == 1:
        return _get_value_for_key(keys[0], obj, default)
    return _get_value_for_keys(keys[1:], _get_value_for_key(keys[0], obj, default), default)


def _get_value_for_key(key, obj, default):
    try:
        return obj[key]
    except (KeyError, AttributeError, IndexError, TypeError):
        try:
            attr = getattr(obj, key)
        except AttributeError:
            return default
        else:
            return attr() if callable(attr) else attr


def create_simple_attributes(service, names):  # pragma: no cover
    exists = len(service.__model__.query.filter(service.__model__.name.in_(names)).all()) > 0
    if not exists:
        for sort_order, name in enumerate(names):
            service.create(sort_order=sort_order,
                           name=name)
