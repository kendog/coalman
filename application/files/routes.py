import os
from flask import Flask, jsonify, request, redirect, url_for, render_template, send_from_directory, send_file
from flask import redirect, render_template, Blueprint, request, url_for
from flask_login import login_required
from flask_security import roles_required, roles_accepted, current_user
from flask import current_app as app
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import File, Tag, TagGroup, Project
from werkzeug.utils import secure_filename
import boto3
import shutil
from sqlalchemy import or_, and_
from io import BytesIO
from .utils import update_file_tags, upload_file, delete_file, get_file


# Blueprint Configuration
files_bp = Blueprint('files_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@files_bp.route('/download/file/<id>')
@login_required
def download_file(id):
    return get_file(id)


@files_bp.route('/error/uploads/<errors>')
@login_required
def error_uploads(errors):
    return render_template('error_uploads.html', errors=errors)


# Files Pages
@files_bp.route('/files')
@roles_accepted('admin','super-admin')
def files():
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_files_bp.files'))

    files = File.query\
        .join(Project)\
        .filter(and_(File.project_id == Project.id, Project.account_id == current_user.account_id))\
        .all()

    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('/files/list.html', files=files, tag_groups=tag_groups)


@files_bp.route('/files/add', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def files_add():
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_files_bp.files_add'))

    if 'submit-add' in request.form:
        # Update Metadata
        file = File(creator_id=current_user.id,project_id=request.form.get('project_id'))
        db.session.add(file)
        db.session.commit()

        file.title = request.form.get('title')
        file.description = request.form.get('description')
        db.session.commit()

        # Update Tags
        update_file_tags(file.id, request.form.getlist('tags'))

        # Upload File
        if 'file' in request.files:
            upload_file(file.id, request.files['file'])

        return redirect(url_for('files_bp.files'))

    return render_template('/files/form.html', template_mode='add')


@files_bp.route('/files/edit/<id>', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def files_edit(id):
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_files_bp.files_edit',id=id))

    file = File.query\
        .join(Project)\
        .filter(and_(File.id == id, File.project_id == Project.id, Project.account_id == current_user.account_id))\
        .first()

    if not file:
        return redirect(url_for('files_bp.files'))

    if 'submit-edit' in request.form:
        if file:
            # Update Metadata
            file.title = request.form.get('title')
            file.description = request.form.get('description')
            db.session.commit()

            # Update Tags
            update_file_tags(file.id, request.form.getlist('tags'))

            # Upload File
            if 'file' in request.files:
                upload_file(file.id, request.files['file'])

        return redirect(url_for('files_bp.files'))

    return render_template('/files/form.html', template_mode='edit', file=file)


@files_bp.route('/files/delete/<id>', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def files_delete(id):
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_files_bp.files_delete',id=id))

    file = File.query\
        .join(Project)\
        .filter(and_(File.id == id, File.project_id == Project.id, Project.account_id == current_user.account_id))\
        .first()

    if not file:
        return redirect(url_for('files_bp.files'))

    if 'submit-delete' in request.form:
        if file:
            db.session.delete(file)
            db.session.commit()
            delete_file(id)
            return redirect(url_for('files_bp.files'))

    return render_template('/files/form.html', template_mode='delete', file=file)
