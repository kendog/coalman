import os
from flask import Flask, jsonify, request, redirect, url_for, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, current_user, login_required, roles_required, utils
from flask_marshmallow import Marshmallow
from werkzeug.utils import secure_filename
import zipfile
from flask_cors import CORS
import datetime
import uuid
import smtplib
import babel
#import re
#import requests
from flask_migrate import Migrate

db = SQLAlchemy()
ma = Marshmallow()

# Create app
def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.config['UPLOAD_FOLDER'] = app.root_path + app.config['UPLOAD_FOLDER']
    db.init_app(app)
    ma.init_app(app)

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    migrate = Migrate(app, db)

    with app.app_context():
            # Include our Routes
            from . import routes

            # Register Blueprints
            app.register_blueprint(auth.auth_bp)
            app.register_blueprint(admin.admin_bp)

            return app



# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Define Schemas
class TagGroupSchema(ma.Schema):
    class Meta:
        model = TagGroup
        # Fields to expose
        fields = ('name', 'tag_id')


class TagSchema(ma.Schema):
    tag_group = ma.Nested(TagGroupSchema)

    class Meta:
        model = Tag
        # Fields to expose
        fields = ('name', 'tag_id', 'tag_group')


class FileSchema(ma.Schema):
    tags = ma.Nested(TagGroupSchema, many=True)

    class Meta:
        model = File
        # Fields to expose
        fields = ('id', 'name', 'title', 'desc', 'tags')


file_schema = FileSchema()
files_schema = FileSchema(many=True)
tag_schema = TagSchema()
tags_schema = TagSchema(many=True)
tag_group_schema = TagGroupSchema()
tag_groups_schema = TagGroupSchema(many=True)


# Most "def" initly needed functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def package_files(uuid):
    package = Package.query.filter_by(uuid=uuid).first()
    package.package_status_id = 2
    db.session.commit()
    zf = zipfile.ZipFile(package.path + package.name, "w", zipfile.ZIP_DEFLATED)
    for file in package.files:
        absname = os.path.abspath(os.path.join(file.path + file.name))
        arcname = absname[len(file.path):]
        zf.write(absname, arcname)
    zf.close()
    package.package_status_id = 3
    db.session.commit()


def send_notification(uuid):
    package = Package.query.filter_by(uuid=uuid).first()
    package.notification_status_id = 2
    db.session.commit()
    # Build the Mail
    message = Message.query.first()
    header = 'From: %s\n' % app.config['MAIL_USERNAME']
    header += 'To: %s\n' % package.user_email
    header += 'Subject: %s\n\n' % message.subject
    message = header + message.message + '\n\n' + package.link;
    # Send the Mail
    server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    results = server.sendmail(app.config['MAIL_USERNAME'], package.user_email, message)

    server.quit()
    #print "results", results
    package.notification_status_id = 3
    db.session.commit()
    return results


# jinja Date Stuff
def format_datetime(value, format='small'):
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="EE MM/dd/y HH:mm"
    elif format == 'small':
        format = "MM/dd/yy HH:mm"
    return babel.dates.format_datetime(value, format)


app.jinja_env.filters['datetime'] = format_datetime


# First Run / Init
@app.before_first_request
def before_first_request():
    if not user_datastore.get_user('admin@beasel.io'):
        encrypted_password = utils.hash_password('admin1234')
        user_datastore.create_user(email='admin@beasel.io',password=encrypted_password)
        db.session.commit()
        user_datastore.add_role_to_user('admin@beasel.io', 'admin')
        db.session.commit()






if __name__ == "__main__":
#    app.run('localhost')
    app.run(host='0.0.0.0')
