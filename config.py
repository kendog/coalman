"""App configuration."""
from os import environ

class Config:
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ['SECRET_KEY']
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    SECURITY_REGISTERABLE = True
    SECURITY_PASSWORD_HASH = os.environ['SECURITY_PASSWORD_HASH']
    SECURITY_PASSWORD_SALT = os.environ['SECURITY_PASSWORD_SALT']
    SECURITY_USER_IDENTITY_ATTRIBUTES = ['email']

    DEBUG = True

    UPLOAD_FOLDER = '/uploads/'
    TEMP_FOLDER = '/tmp/'
    ALLOWED_EXTENSIONS = set(['pdf', 'PDF', 'png', 'PNG'])
    DOWNLOAD_PROTOCOL = 'https'
    DOWNLOAD_DOMAIN = 'coalman.io'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']

    SITE_ADMIN_EMAIL = os.environ['SITE_ADMIN_EMAIL']
    SITE_ADMIN_PASSWORD = os.environ['SITE_ADMIN_PASSWORD']

    UPLOAD_TO_S3 = True
    AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
    AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']
    S3_BUCKET = 'S3_BUCKET'
    S3_URL = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

    IN_MEMORY_PACKAGE = True
    DISK_PACKAGE_CACHING = False
