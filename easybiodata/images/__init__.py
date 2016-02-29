from easybiodata.core import Service
from easybiodata.images.models import Images
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from easybiodata.utils.s3_upload import upload_with_boto


class ImageService(Service):
    __model__ = Images

    def upload_image_with_boto(self, image_request, user):
        from easybiodata.services import files

        if len(image_request.files) != 1:
            raise BadRequest('Must send exactly one file')

        sent_file = next(image_request.files.values())
        file_data = sent_file.stream.read()
        _, mimetype = files.validate_and_extract_mimetype(file_data, sent_file.filename)

        if mimetype in ['image/png', 'image/gif', 'image/jpeg']:

            return upload_with_boto(file_data, 'image', sent_file)

        raise UnsupportedMediaType()
