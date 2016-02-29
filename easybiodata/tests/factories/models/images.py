import datetime
import os

import factory

from easybiodata.images import Images
from easybiodata.utils.s3_upload import _s3_key_for_data


class ImageFactory(factory.Factory):
    class Meta:
        model = Images

    creator = None

    deleted_at = factory.Iterator([datetime.datetime.now(tz=datetime.timezone.utc), None])

    notes = factory.Faker('sentence')

    bucket_name = 'easybiodata-file-uploads'
    key = factory.LazyAttribute(lambda _: _s3_key_for_data(os.urandom(20), 'entity-id', 'orig_filename.jpg'))

    size_bytes = factory.Faker('random_int', min=1, max=10000)
