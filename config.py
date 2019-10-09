"""App configuration."""
from os import environ

class Config:
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_DATABASE_URI = 'postgres://postgresql:TD7U5wYNYsJRBFBG@postgresql-dev.cfiolaaedchf.us-west-2.rds.amazonaws.com:5432/beasel3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secret_key'
    JWT_SECRET_KEY = 'jwt_secret_key'
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
