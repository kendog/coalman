import os
from flask import redirect, render_template, Blueprint, request, url_for, send_from_directory, send_file
from flask_login import login_required
from flask import current_app as app
from flask_security import roles_required
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..models import db, Package, File
import uuid
import smtplib
import boto3
import zipfile
import codecs
import json
from io import BytesIO

s3_client = boto3.client(
   "s3",
   aws_access_key_id=app.config['AWS_ACCESS_KEY'],
   aws_secret_access_key=app.config['AWS_SECRET_KEY']
)

# Blueprint Configuration
packages_bp = Blueprint('packages_bp', __name__,
                    template_folder='templates',
                    static_folder='static')
#compile_auth_assets(app)


@packages_bp.route('/packages/<uuid>')
def download_package(uuid):

    package = Package.query.filter_by(uuid=uuid).first()
    package.package_status_id = 2
    db.session.commit()

    if app.config['IN_MEMORY_PACKAGE']:
        return send_file(get_package_memory(package), attachment_filename=package.name, as_attachment=True)

    if os.path.isfile(package.path + package.name) and app.config['DISK_PACKAGE_CACHING']:
        # File does exist...  SKIP Create Package
        return send_from_directory(package.path, package.name)
    else:
        create_package_file(package)
        return send_from_directory(package.path, package.name)


    package.downloads += 1
    package.package_status_id = 3
    db.session.commit()


def create_package_file(package):


        zf = zipfile.ZipFile(package.path + package.name, "w", zipfile.ZIP_DEFLATED)
        for file in package.files:
            if app.config['UPLOAD_TO_S3']:
                response = s3_client.get_object(Bucket=app.config['S3_BUCKET'], Key=file.s3_key)
                zf.writestr(file.name, response['Body'].read())
            else:
                absname = os.path.abspath(os.path.join(file.path + file.name))
                zf.write(absname, file.name)
        zf.close()


def get_package_memory(package):
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for file in package.files:
            if app.config['UPLOAD_TO_S3']:
                response = s3_client.get_object(Bucket=app.config['S3_BUCKET'], Key=file.s3_key)
                zf.writestr(file.name, response['Body'].read())
            else:
                absname = os.path.abspath(os.path.join(file.path + file.name))
                in_file = open(absname, "rb") # opening for [r]eading as [b]inary
                data = in_file.read() # if you only wanted to read 512 bytes, do .read(512)
                in_file.close()
                zf.writestr(file.name, data)
    memory_file.seek(0)
    return memory_file


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


@packages_bp.route('/packages')
@login_required
def packages():
    packages = Package.query.all()
    return render_template('packages/list.html', packages=packages)


@packages_bp.route('/packages/add', methods=['POST', 'GET'])
@login_required
def packages_add():
    if 'submit-add' in request.form:
        # Update Metadata
        recipient_name = request.form.get('recipient_name')
        recipient_email = request.form.get("recipient_email")
        file_ids = request.form.getlist("files")

        package = Package(uuid=str(uuid.uuid4()), recipient_name=recipient_name, recipient_email=recipient_email)
        db.session.add(package)
        db.session.commit()

        package.package_status_id = 1
        package.notification_status_id = 1
        package.name = package.uuid + ".zip"
        package.path = app.config['TEMP_FOLDER']
        package.link = app.config['DOWNLOAD_PROTOCOL'] + '://' + app.config['DOWNLOAD_DOMAIN'] + url_for(
            'packages_bp.download_package', uuid=package.uuid)
        db.session.commit()

        # Add Files
        for item in file_ids:
            #print item
            exists = db.session.query(File.id).filter_by(id=item).scalar()
            if exists:
                package.files.append(File.query.filter_by(id=item).first())
                db.session.commit()

        # Send Email
        if request.form.get("notify"):
            send_notification(package.uuid)

        return redirect(url_for('packages_bp.packages'))
    files = File.query.all()
    return render_template('packages/form.html', template_mode='add', files=files)


@packages_bp.route('/packages/edit/<id>', methods=['POST', 'GET'])
@login_required
def packages_edit(id):
    package = Package.query.filter_by(id=id).first()
    if 'submit-edit' in request.form:
        # Update Metadata
        recipient_name = request.form.get('recipient_name')
        recipient_email = request.form.get("recipient_email")
        file_ids = request.form.getlist("files")

        package.recipient_name = recipient_name
        package.recipient_email = recipient_email
        package.files[:] = []
        db.session.commit()

        # Add Files
        for item in file_ids:
            #print item
            exists = db.session.query(File.id).filter_by(id=item).scalar()
            if exists:
                package.files.append(File.query.filter_by(id=item).first())
                db.session.commit()

        # Send Email
        if request.form.get("notify"):
            send_notification(package.uuid)

        return redirect(url_for('packages_bp.packages'))
    files = File.query.all()
    return render_template('packages/form.html', template_mode='edit', package=package, files=files)


@packages_bp.route('/packages/delete/<id>', methods=['POST', 'GET'])
@login_required
def packages_delete(id):
    package = Package.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if package:
            db.session.delete(package)
            db.session.commit()
            return redirect(url_for('packages_bp.packages'))
    return render_template('packages/form.html', template_mode='delete', package=package)
