"""App configuration."""
from os import environ

class Config:
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_DATABASE_URI = 'postgres://postgresql:TD7U5wYNYsJRBFBG@postgresql-dev.cfiolaaedchf.us-west-2.rds.amazonaws.com:5432/beasel3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secret_key'
    SECURITY_REGISTERABLE = True
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = 'password_salt'
    SECURITY_USER_IDENTITY_ATTRIBUTES = ['email']
    DEBUG = True

    UPLOAD_FOLDER = '/uploads/'
    TEMP_FOLDER = '/tmp/'
    ALLOWED_EXTENSIONS = set(['pdf', 'PDF', 'png', 'PNG'])
    DOWNLOAD_PROTOCOL = 'https'
    DOWNLOAD_DOMAIN = 'beasel.io'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'admin@juniperebc.com'
    MAIL_PASSWORD = 'kcDR1776'

    """Set Flask configuration vars from .env file.

    # General Config
    SECRET_KEY = environ.get('SECRET_KEY')
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get('FLASK_ENV')

    # Flask-Session
    SESSION_TYPE = environ.get('SESSION_TYPE')
    SESSION_REDIS = redis.from_url(environ.get('SESSION_REDIS'))

    # Flask-Assets
    LESS_BIN = environ.get('LESS_BIN')
    ASSETS_DEBUG = environ.get('ASSETS_DEBUG')
    LESS_RUN_IN_DEBUG = environ.get('LESS_RUN_IN_DEBUG')

    # Static Assets
    STATIC_FOLDER = environ.get('STATIC_FOLDER')
    TEMPLATES_FOLDER = environ.get('TEMPLATES_FOLDER')
    COMPRESSOR_DEBUG = environ.get('COMPRESSOR_DEBUG')

    # Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')
    """
