from marshmallow import validate, fields

from easybiodata.constants import easybiodata_MAX_NOTES_LENGTH
from easybiodata.utils.schema import easybiodataSchema
from easybiodata.services import files


def _file_to_html(obj):
    return files.generate_url(obj)


class ImagesRequestSchema(easybiodataSchema):
    title = fields.String(validate=validate.Length(1, easybiodata_MAX_NOTES_LENGTH))
    body = fields.String(validate=validate.Length(1, easybiodata_MAX_NOTES_LENGTH))


class ImageResponseSchema(easybiodataSchema):
    id = fields.Function(lambda o: o.id)
    title = fields.Function(lambda o: o.title)
    body = fields.Function(lambda o: o.body)


class AllImagesResponseSchema(easybiodataSchema):
    images = fields.Function(lambda o: [(doc.id, doc.title, doc.body) for doc in o])


class ImageFilesResponseSchema(easybiodataSchema):
    imageId = fields.Function(lambda o: o.id)
    imageUrl = fields.Function(_file_to_html)
