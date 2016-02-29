import pytest

from easybiodata.tests.utils.request_helpers import get_json, put_json, validate_response, put_data
from easybiodata.services import images
from easybiodata.tests.functional.resources.v1.common import VALID_FILES, input_file
from easybiodata.services import images, files


VALID_IMAGE_FILES = ['Lenna.png',
                   'Lenna.jpg',
                   'Lenna.gif']

INVALID_IMAGE_FILES = ['test.doc',
                     'test.pdf',
                     'test.xls',
                     'random_data']


@pytest.mark.parametrize('file_name', VALID_FILES)
@pytest.mark.parametrize('file_path', VALID_IMAGE_FILES)
def test_load_valid_image_file(test_client, file_name, file_path, random_user, upload_with_boto):
    with input_file(file_path, mode='rb') as f:
        rv = put_data(test_client, '/v1/images/files', {file_name: (f, file_name)})
    validate_response(rv, success_status=200)

    fileId = rv.json['imageId']
    my_file = images.get(fileId)
    assert my_file
    assert rv.json['imageUrl'] == files.generate_url(my_file)

    assert upload_with_boto.call_count == 1
    (_, _, file), _ = upload_with_boto.call_args
    assert file_name == file.filename


@pytest.mark.parametrize('file_name', VALID_IMAGE_FILES)
@pytest.mark.parametrize('file_path', INVALID_IMAGE_FILES)
def test_load_invalid_image_file(test_client, file_name, file_path, random_user, upload_with_boto):

    with input_file(file_path, mode='rb') as f:
        rv = put_data(test_client, '/v1/images/files', {file_name: (f, file_name)})
        validate_response(rv, failure_status=415)

    assert upload_with_boto.call_count == 0
