import os
from flask import Flask, jsonify, request, redirect, url_for, render_template, send_from_directory
from flask import redirect, render_template, Blueprint, request, url_for
from flask_login import login_required
from flask_security import roles_required, roles_accepted, current_user
from flask import current_app as app
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import File, Tag, TagGroup, Project
from sqlalchemy import or_, and_
from .utils import update_file_tags, upload_file, delete_file



# Blueprint Configuration
manage_files_bp = Blueprint('manage_files_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/manage')


# Files Pages
@manage_files_bp.route('/files')
@roles_required('super-admin')
def files():
    files = File.query.all()
    tag_groups = TagGroup.query.order_by(TagGroup.weight).all()
    return render_template('/files/manage/list.html', files=files, tag_groups=tag_groups)


@manage_files_bp.route('/files/add', methods=['POST', 'GET'])
@roles_required('super-admin')
def files_add():
    if 'submit-add' in request.form:
        # Create File
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

        return redirect(url_for('manage_files_bp.files'))

    return render_template('/files/manage/form.html', template_mode='add')


@manage_files_bp.route('/files/edit/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def files_edit(id):
    file = File.query.filter_by(id=id).first()
    if 'submit-edit' in request.form:
        if file:
            file.title = request.form.get('title')
            file.description = request.form.get('description')
            db.session.commit()

            # Update Tags
            update_file_tags(file.id, request.form.getlist('tags'))

            # Upload File
            if 'file' in request.files:
                upload_file(file.id, request.files['file'])

            return redirect(url_for('manage_files_bp.files'))

    return render_template('/files/manage/form.html', template_mode='edit', file=file)


@manage_files_bp.route('/files/delete/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def files_delete(id):
    file = File.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        file = File.query.filter_by(id=id).first()
        if file:
            db.session.delete(file)
            db.session.commit()
            delete_file(id)
            return redirect(url_for('manage_files_bp.files'))

    return render_template('/files/manage/form.html', template_mode='delete', file=file)
