import os
from flask import redirect, render_template, Blueprint, request, url_for, send_from_directory, send_file
from flask_login import login_required, current_user
from flask import current_app as app
from flask_security import roles_required
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import Archive, File, Project
import uuid
import boto3
import zipfile
import codecs
import json
from io import BytesIO
from ..notifications.utils import create_notification
#from .utils import create_notification, send_email_notification, send_sms_notification

# Blueprint Configuration
manage_archives_bp = Blueprint('manage_archives_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/manage')
#compile_auth_assets(app)



@manage_archives_bp.route('/archives')
@roles_required('super-admin')
def archives():
    archives = Archive.query.all()
    return render_template('/archives/manage/list.html', archives=archives)


@manage_archives_bp.route('/archives/add', methods=['POST', 'GET'])
@roles_required('super-admin')
def archives_add():
    if 'submit-add' in request.form:
        # Update Metadata
        file_ids = request.form.getlist("files")

        archive = Archive(uuid=str(uuid.uuid4()), creator_id=current_user.id,project_id=request.form.get('project_id'))
        db.session.add(archive)
        db.session.commit()

        archive.status_name = "created"

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
        #if request.form.get("notify"):
            #create_notification(2, 1, True, False)

        return redirect(url_for('manage_archives_bp.archives'))
    files = File.query.all()
    return render_template('/archives/manage/form.html', template_mode='add', files=files)


@manage_archives_bp.route('/archives/edit/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def archives_edit(id):
    archive = Archive.query.filter_by(id=id).first()
    if 'submit-edit' in request.form:
        # Update Metadata
        file_ids = request.form.getlist("files")
        archive.files[:] = []
        db.session.commit()

        archive.status_name = "created"

        # Add Files
        for file_id in file_ids:
            #print item
            file = File.query.filter_by(id=file_id).first()
            if file and archive:
                archive.files.append(file)
                db.session.commit()

        # Send Email
        #if request.form.get("notify"):
        #    create_notification(2, 1, True, False)

        return redirect(url_for('manage_archives_bp.archives'))
    files = File.query.all()
    return render_template('/archives/manage/form.html', template_mode='edit', archive=archive, files=files)


@manage_archives_bp.route('/archives/delete/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def archives_delete(id):
    archive = Archive.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if archive:
            db.session.delete(archive)
            db.session.commit()
            return redirect(url_for('manage_archives_bp.archives'))
    files = File.query.all()
    return render_template('/archives/manage/form.html', template_mode='delete', archive=archive, files=files)
