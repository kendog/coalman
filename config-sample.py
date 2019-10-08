"""App configuration."""
from os import environ

class Config:
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_DATABASE_URI = 'db_protocol://user:pass@host:port/database'
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
    DOWNLOAD_DOMAIN = 'coalman.io'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'username'
    MAIL_PASSWORD = 'password'
