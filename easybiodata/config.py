import base64
import datetime
import os


class Config(object):
    DEPLOYMENT_WIPE_DB = False
    DEPLOYMENT_CREATE_TEST_DATA = False
    ERROR_404_HELP = False
    easybiodata_UPLOADS_BUCKET = 'easybiodata-file-uploads'
    easybiodata_UPLOADS_URL = 'https://files.easybiodata.com'
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    # MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = datetime.timedelta(hours=24)
    RESTFUL_JSON = {'separators': (',', ':'), 'indent': None, 'sort_keys': False}
    SECRET_KEY = 'secret-key'
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    easybiodata_UPLOADS_BUCKET = 'easybiodata-file-uploads'


class LocalConfig(Config):
    DEBUG = True
    easybiodata_UPLOADS_BUCKET = 'easybiodata-file-uploads'
    easybiodata_UPLOADS_URL = 'https://s3.amazonaws.com/easybiodata-file-uploads/'
    easybiodata_SERVER_URL = 'http://localhost:5000'
    REMEMBER_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql:///easybiodata')
    

class TestingConfig(LocalConfig):
    LOGIN_DISABLED = False
    TESTING = True


class ProductionConfig(Config):
    pass

config = {
    'local': LocalConfig,
    'testing': TestingConfig,
    'prod': ProductionConfig
}
