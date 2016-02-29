import re
from easybiodata.identifiers import ID_ALPHABET


def create_object_json_schema(properties, optional=None):
    if optional is None:
        optional = []
    if isinstance(optional, str):
        optional = [optional]
    return {
        'type'                : 'object',
        'properties'          : properties,
        'required'            : [prop for prop in properties.keys() if prop not in optional],
        'additionalProperties': False
    }


def id_string():
    return string_with_pattern('^[{}]+$'.format(re.escape(ID_ALPHABET)))


def string_with_pattern(pattern):
    return {'type'   : 'string',
            'pattern': pattern}


def string_with_length(min=1, max=None):
    d = {'type': 'string'}
    if min is not None:
        d['minLength'] = min
    if max is not None:
        d['maxLength'] = max
    return d


def string_with_enum(enum):
    return {'type': 'string',
            'enum': enum}


def number_with_enum(enum):
    return {'type': 'number',
            'enum': enum}


def number_with_range(min, max):
    d = {'type': 'number'}
    if min is not None:
        d['minimum'] = min
    if max is not None:
        d['maximum'] = max
    return d


def nullable(type):
    return {'oneOf': [{'type': 'null'},
                      type]}
