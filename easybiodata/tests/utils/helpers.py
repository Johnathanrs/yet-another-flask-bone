import importlib
import random
import string

from easybiodata.identifiers import ID_ALPHABET


def fake_id():
    return ''.join(random.sample(ID_ALPHABET, len(ID_ALPHABET)))


def fake_load_id():
    return '-'.join([random.randint(1, 1000),
                     random.sample(ID_ALPHABET, 3),
                     random.sample(string.ascii_letters, 3)])


def nullable_field_names(schema_module, schema_class_name):
    module = importlib.import_module(schema_module)
    klass = getattr(module, schema_class_name)
    return [name for name, field in klass().fields.items() if field.allow_none and not field.dump_only]


def nullable_attribute_names(schema_module, schema_class_name):
    def get_attribute_name(field_name, field):
        attribute = field.attribute
        return attribute if attribute is not None else field_name

    module = importlib.import_module(schema_module)
    schema = getattr(module, schema_class_name)()
    return [get_attribute_name(field_name, field) for field_name, field in schema.fields.items()
            if field.allow_none and not field.dump_only]
