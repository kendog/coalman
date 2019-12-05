import os

class Config:
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ['SECRET_KEY']
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']

    SECURITY_PASSWORD_HASH = os.environ['SECURITY_PASSWORD_HASH']
    SECURITY_PASSWORD_SALT = os.environ['SECURITY_PASSWORD_SALT']
    SECURITY_USER_IDENTITY_ATTRIBUTES = ['email']
    SECURITY_REGISTERABLE = False
    SECURITY_RECOVERABLE = True
    SECURITY_EMAIL_SENDER = os.environ['MAIL_DEFAULT_SENDER']

    DEBUG = True

    UPLOAD_FOLDER = '/uploads/'
    UPLOADED_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')

    TEMP_FOLDER = '/tmp/'
    ALLOWED_EXTENSIONS = set(['pdf', 'png'])
    DOWNLOAD_PROTOCOL = 'https'
    DOWNLOAD_DOMAIN = 'bbcore.coalman.io'

    MAIL_SERVER = 'email-smtp.us-west-2.amazonaws.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    MAIL_DEFAULT_SENDER = os.environ['MAIL_DEFAULT_SENDER']

    SUPER_ADMIN_EMAIL = os.environ['SUPER_ADMIN_EMAIL']
    SUPER_ADMIN_PASSWORD = os.environ['SUPER_ADMIN_PASSWORD']

    UPLOAD_TO_S3 = True
    AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
    AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']
    S3_BUCKET = os.environ['S3_BUCKET']
    S3_URL = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

    IN_MEMORY_ARCHIVES = True
    LOCAL_CACHING = False

    DROPZONE_REDIRECT_VIEW='dropzone_bp.completed'  # set redirect view
    DROPZONE_MAX_FILES=1
    #DROPZONE_UPLOAD_ON_CLICK=True

    S3_BUCKET_SPECS = os.environ['S3_BUCKET_SPECS']
    S3_BUCKET_SPECS_PAGES = os.environ['S3_BUCKET_SPECS_PAGES']
