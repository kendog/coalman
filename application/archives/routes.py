import os
from flask import redirect, render_template, Blueprint, request, url_for, send_from_directory, send_file
from flask_login import login_required
from flask import current_app as app
from flask_security import roles_required
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..models import db, Archive, File
import uuid
import boto3
import zipfile
import codecs
import json
from io import BytesIO
from ..notifications import send_notification

s3_client = boto3.client(
   "s3",
   aws_access_key_id=app.config['AWS_ACCESS_KEY'],
   aws_secret_access_key=app.config['AWS_SECRET_KEY']
)

# Blueprint Configuration
archives_bp = Blueprint('archives_bp', __name__,
                    template_folder='templates',
                    static_folder='static')
#compile_auth_assets(app)


@archives_bp.route('/archives/<uuid>')
def download_archive(uuid):

    archive = Archive.query.filter_by(uuid=uuid).first()
    archive.archive_status_id = 2
    db.session.commit()

    if app.config['IN_MEMORY_ARCHIVES']:
        return send_file(get_archive_memory(archive), attachment_filename=archive.name, as_attachment=True)

    if os.path.isfile(archive.path + archive.name) and app.config['DISK_PACKAGE_CACHING']:
        # File does exist...  SKIP Create Archive
        return send_from_directory(archive.path, archive.name)
    else:
        create_archive_file(archive)
        return send_from_directory(archive.path, archive.name)


    archive.downloads += 1
    archive.archive_status_id = 3
    db.session.commit()


def create_archive_file(archive):


        zf = zipfile.ZipFile(archive.path + archive.name, "w", zipfile.ZIP_DEFLATED)
        for file in archive.files:
            if app.config['UPLOAD_TO_S3']:
                response = s3_client.get_object(Bucket=app.config['S3_BUCKET'], Key=file.s3_key)
                zf.writestr(file.name, response['Body'].read())
            else:
                absname = os.path.abspath(os.path.join(file.path + file.name))
                zf.write(absname, file.name)
        zf.close()


def get_archive_memory(archive):
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for file in archive.files:
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




@archives_bp.route('/archives')
@login_required
def archives():
    archives = Archive.query.all()
    return render_template('archives/list.html', archives=archives)


@archives_bp.route('/archives/add', methods=['POST', 'GET'])
@login_required
def archives_add():
    if 'submit-add' in request.form:
        # Update Metadata
        recipient_name = request.form.get('recipient_name')
        recipient_email = request.form.get("recipient_email")
        file_ids = request.form.getlist("files")

        archive = Archive(uuid=str(uuid.uuid4()), recipient_name=recipient_name, recipient_email=recipient_email)
        db.session.add(archive)
        db.session.commit()

        archive.archive_status_id = 1
        archive.notification_status_id = 1
        archive.name = archive.uuid + ".zip"
        archive.path = app.config['TEMP_FOLDER']
        archive.link = app.config['DOWNLOAD_PROTOCOL'] + '://' + app.config['DOWNLOAD_DOMAIN'] + url_for(
            'archives_bp.download_archive', uuid=archive.uuid)
        db.session.commit()

        # Add Files
        for item in file_ids:
            #print item
            exists = db.session.query(File.id).filter_by(id=item).scalar()
            if exists:
                archive.files.append(File.query.filter_by(id=item).first())
                db.session.commit()

        # Send Email
        if request.form.get("notify"):
            send_notification(archive.uuid)

        return redirect(url_for('archives_bp.archives'))
    files = File.query.all()
    return render_template('archives/form.html', template_mode='add', files=files)


@archives_bp.route('/archives/edit/<id>', methods=['POST', 'GET'])
@login_required
def archives_edit(id):
    archive = Archive.query.filter_by(id=id).first()
    if 'submit-edit' in request.form:
        # Update Metadata
        recipient_name = request.form.get('recipient_name')
        recipient_email = request.form.get("recipient_email")
        file_ids = request.form.getlist("files")

        archive.recipient_name = recipient_name
        archive.recipient_email = recipient_email
        archive.files[:] = []
        db.session.commit()

        # Add Files
        for item in file_ids:
            #print item
            exists = db.session.query(File.id).filter_by(id=item).scalar()
            if exists:
                archive.files.append(File.query.filter_by(id=item).first())
                db.session.commit()

        # Send Email
        if request.form.get("notify"):
            send_notification(archive.uuid)

        return redirect(url_for('archives_bp.archives'))
    files = File.query.all()
    return render_template('archives/form.html', template_mode='edit', archive=archive, files=files)


@archives_bp.route('/archives/delete/<id>', methods=['POST', 'GET'])
@login_required
def archives_delete(id):
    archive = Archive.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if archive:
            db.session.delete(archive)
            db.session.commit()
            return redirect(url_for('archives_bp.archives'))
    return render_template('archives/form.html', template_mode='delete', archive=archive)
