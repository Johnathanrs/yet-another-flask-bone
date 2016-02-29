import mimetypes
import unicodedata
import urllib.parse

import magic
from flask import current_app, request
from flask.ext.login import current_user

from easybiodata.core import Service
from easybiodata.files.models import File
from easybiodata.utils.helpers import create_simple_attributes
from easybiodata.utils.s3_upload import upload_s3, delete_s3, _s3_key_for_data, upload_with_boto

BANNED_EXTENSIONS = ['ade', 'adp', 'bat', 'chm', 'cmd', 'com', 'cpl', 'exe', 'hta', 'ins', 'isp', 'jar', 'jse', 'lib',
                     'lnk', 'mde', 'msc', 'msp', 'mst', 'pif', 'scr', 'sct', 'shb', 'sys', 'vb', 'vbe', 'vbs', 'vxd',
                     'wsc', 'wsf', 'wsh']
BANNED_MIMETYPES = ['application/x-dosexec', 'text/x-msdos-batch']


class FileService(Service):
    __model__ = File

    @staticmethod
    def validate_and_extract_mimetype(data, filename):
        def extract_extension(filename):
            _, *ext = filename.rsplit('.', 1)
            return ext[0].lower() if len(ext) > 0 else None

        def guess_mimetype(data):
            mime_bytes = magic.from_buffer(data[:1024], mime=True)
            return mime_bytes.decode('utf8') if mime_bytes is not None else None

        actual_extension = extract_extension(filename)
        if actual_extension in BANNED_EXTENSIONS:
            return False, None

        mimetype = guess_mimetype(data)

        current_app.logger.info('Detected mimetype: {}'.format(mimetype))
        if mimetype in BANNED_MIMETYPES:
            return False, None

        guessed_extension = mimetypes.guess_extension(mimetype)
        if guessed_extension in BANNED_EXTENSIONS:
            current_app.logger.info('Guessed extension {} is banned'.format(guessed_extension))
            return False, None

        return True, mimetype

    @staticmethod
    def _original_file_name(file):
        return file.key.split('_', 3)[3]


    def create_file_from_upload(self, data, filename, creator, prefix):
        def secure_filename(filename):
            filename = unicodedata.normalize('NFKD', filename)
            for sep in magic.os.path.sep, magic.os.path.altsep, '/', '\\':
                if sep is not None:
                    filename = filename.replace(sep, ' ')

            return '_'.join(filename.split()).strip('._')

        filename = urllib.parse.unquote(filename, errors='ignore')
        current_app.logger.info('File uploaded: {}, Length: {}'.format(filename, request.content_length))

        secured_filename = secure_filename(filename)
        if len(secured_filename) == 0:
            current_app.logger.info('Invalid filename: {}'.format(filename))
            return None

        valid, mimetype = self.validate_and_extract_mimetype(data, filename)
        if not valid:
            return None

        bucket_name = current_app.config['easybiodata_UPLOADS_BUCKET']

        key = upload_s3(bucket_name,
                        data,
                        mimetype,
                        prefix,
                        filename)

        return self.create(creator=creator,
                           bucket_name=bucket_name,
                           size_bytes=len(data),
                           key=key)


    def create_image_file_from_upload(self, image_request, user):
        from easybiodata.services import files
        from werkzeug.exceptions import BadRequest, UnsupportedMediaType

        if len(image_request.files) != 1:
            raise BadRequest('Must send exactly one file')

        sent_file = next(image_request.files.values())
        file_data = sent_file.stream.read()
        _, mimetype = files.validate_and_extract_mimetype(file_data, sent_file.filename)

        if mimetype in ['image/png', 'image/gif', 'image/jpeg']:            
            file = files.create_file_from_upload(file_data,
                                                 sent_file.filename,
                                                 user,
                                                 'logo')

            if file is None:
                raise UnsupportedMediaType()

            return file

        raise UnsupportedMediaType()


    def generate_url(self, file):
        return urllib.parse.urljoin(current_app.config['easybiodata_UPLOADS_URL'],
                                    urllib.parse.quote(file.key, errors='ignore'))


    def update_file(self, file, async, **kwargs):

        self.update(file, commit=True, **kwargs)

        return file

    def delete_file(self, file, async):
        import datetime

        delete_s3(file.bucket_name, file.key)
        file.deleted_at = datetime.datetime.now(tz=datetime.timezone.utc)
        self.save(file)

        return file
