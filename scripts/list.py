from boto.s3.connection import S3Connection

conn = S3Connection('AKIAJFDM6ELQEJKGHBCA','Lrl+a5ky+/9wlPQbIiKO8YRHVJRANW4edHndzffB')
bucket = conn.get_bucket('easybiodata-production-singapore')
for key in bucket.list():
    print key.name.encode('utf-8')
