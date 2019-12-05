"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_required
from flask import current_app as app
from flask_security import roles_required, roles_accepted, current_user
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import User, Account, Project
from sqlalchemy import or_, and_
from datetime import datetime


# Blueprint Configuration
projects_bp = Blueprint('projects_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@projects_bp.route('/project/<id>')
@login_required
def project(id):
    project = Project.query.filter_by(id=id).first()
    return render_template('/projects/home.html', project=project)


@projects_bp.route('/projects')
@roles_accepted('admin','super-admin')
@login_required
def projects():
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_projects_bp.projects'))

    return render_template('/projects/list.html')


@projects_bp.route('/projects/add', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def projects_add():

    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_projects_bp.projects_add'))

    if 'submit-add' in request.form:
        duedate = datetime.strptime(request.form['duedate'] + " 00:00:00", "%m/%d/%Y %H:%M:%S")
        project = Project(name=request.form['name'], duedate=request.form['duedate'], account_id=current_user.account_id, creator_id=current_user.id)
        db.session.add(project)
        db.session.commit()
        # Add Users
        user_ids = request.form.getlist("user_ids")
        for user_id in user_ids:
            exists = db.session.query(User.id).filter_by(id=user_id).scalar()
            if exists:
                project.users.append(User.query.filter_by(id=user_id).first())
                db.session.commit()
        return redirect(url_for('projects_bp.projects'))
    return render_template('/projects/form.html', template_mode='add')


@projects_bp.route('/projects/edit/<id>', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def projects_edit(id):

    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_projects_bp.projects_edit',id=id))

    project = Project.query\
        .join(Account)\
        .filter(and_(Project.id == id, Account.id == Project.account_id, Account.id == current_user.account_id))\
        .first()

    if not project:
        return redirect(url_for('projects_bp.projects'))

    if 'submit-edit' in request.form:
        if project:
            project.name = request.form['name']
            project.duedate = request.form['duedate']
            project.account_id = current_user.account_id
            project.users[:] = []
            db.session.commit()
            # Add Users
            user_ids = request.form.getlist("user_ids")
            for user_id in user_ids:
                exists = db.session.query(User.id).filter_by(id=user_id).scalar()
                if exists:
                    project.users.append(User.query.filter_by(id=user_id).first())
                    db.session.commit()
        return redirect(url_for('projects_bp.projects'))
    return render_template('/projects/form.html', template_mode='edit', project=project)


@projects_bp.route('/projects/delete/<id>', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def projects_delete(id):

    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_projects_bp.projects_delete',id=id))

    project = Project.query\
        .join(Account)\
        .filter(and_(Project.id == id, Account.id == Project.account_id, Account.id == current_user.account_id))\
        .first()

    if not project:
        return redirect(url_for('projects_bp.projects'))

    if 'submit-delete' in request.form:
        if project:
            db.session.delete(project)
            db.session.commit()
        return redirect(url_for('projects_bp.projects'))
    return render_template('/projects/form.html', template_mode='delete', project=project)
