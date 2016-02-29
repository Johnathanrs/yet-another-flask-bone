from functools import wraps

from flask import request, g
from werkzeug.exceptions import BadRequest

from easybiodata import api


def _validate_json():
    request_json = request.get_json()
    if request_json is None:
        raise BadRequest('Incorrect content type or nothing sent in request')
    return request_json


def with_json_request():
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            _validate_json()
            return f(*args, **kwargs)
        return wrapper
    return decorator


def with_request_schema(schema):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            _validate_json()
            data, errors = schema.load(request.get_json())
            if len(errors) > 0:
                raise BadRequest(errors)
            g.deserialized = data
            return f(*args, **kwargs)
        return wrapper
    return decorator


def with_response_schema(schema):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            rv = f(*args, **kwargs)
            status_code = headers = None
            if isinstance(rv, tuple):
                rv, status_code, headers = rv + (None,) * (3 - len(rv))
            return api.make_response(schema.dump(rv).data, code=status_code, headers=headers)
        return wrapper
    return decorator
