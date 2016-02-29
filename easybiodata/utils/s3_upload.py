import hashlib
import os

import boto3
from flask import current_app
import hashids


def upload_s3(bucket_name, data, mimetype, prefix, suffix):
    key = _s3_key_for_data(data, prefix, suffix)
    _do_upload(bucket_name, data, key, mimetype)
    return key


def _do_upload(bucket_name, data, key, mimetype):
    current_app.logger.info('Storing file {} [{}] in bucket {}'.format(key, mimetype, bucket_name))
    s3 = boto3.resource('s3')
    s3.Object(bucket_name, key).put(Body=data,
                                    CacheControl='public, max-age=31536000',
                                    ContentType=mimetype)


def delete_s3(bucket_name, key):
    current_app.logger.info('Deleting file {} from bucket {}'.format(key, bucket_name))
    s3 = boto3.resource('s3')
    s3.Object(bucket_name, key).delete()


def _s3_key_for_data(data, prefix, suffix):
    if data is None:
        raise ValueError('data must not be None')
    if prefix is None or len(prefix) == 0:
        raise ValueError('Must pass prefix')
    if suffix is None or len(suffix) == 0:
        raise ValueError('Must pass suffix')

    if isinstance(data, str):
        data = data.encode()

    h = hashids.Hashids()
    short_hash = h.encode(int.from_bytes(hashlib.sha1(data).digest(), byteorder='little'))
    fun_str = h.encode(int.from_bytes(os.urandom(4), byteorder='little'))

    key = '{}_{}_{}_{}'.format(prefix, short_hash, fun_str, suffix)

    if len(key) > 1024:
        raise ValueError('Generated key length exceeds 1024')
    return key

def upload_with_boto(file_data, prefix, sent_file):
    from easybiodata.services import images,files
    from flask_login import current_user
    import boto
    from boto.s3.key import Key


    bucket_name = 'easybiodata-file-uploads'
    conn = boto.connect_s3(os.environ['AWS_ACCESS_ID'],
                           os.environ['AWS_SECRET_KEY'])
    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)

    k.key = _s3_key_for_data(file_data, prefix, sent_file.filename)
    sent_file.seek(0)
    k.set_contents_from_file(sent_file)
    k.make_public()

    return images.create(creator=current_user,
                         bucket_name=bucket_name,
                         size_bytes=len(file_data),
                         key=k.key)
