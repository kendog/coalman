"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_required
from flask import current_app as app
from flask_security import roles_required, roles_accepted, current_user
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import Project, Account, User
from datetime import datetime

# Blueprint Configuration
manage_projects_bp = Blueprint('manage_projects_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/manage')


@manage_projects_bp.route('/projects')
@roles_required('super-admin')
def projects():
    return render_template('/projects/manage/list.html')


@manage_projects_bp.route('/projects/add', methods=['POST', 'GET'])
@roles_required('super-admin')
def projects_add():
    if 'submit-add' in request.form:
        duedate = datetime.strptime(request.form['duedate'] + " 00:00:00", "%m/%d/%Y %H:%M:%S")
        project = Project(name=request.form['name'], duedate=request.form['duedate'], account_id=request.form['account_id'], creator_id=current_user.id)
        db.session.add(project)
        db.session.commit()
        # Add Users
        user_ids = request.form.getlist("user_ids")
        for user_id in user_ids:
            exists = db.session.query(User.id).filter_by(id=user_id).scalar()
            if exists:
                project.users.append(User.query.filter_by(id=user_id).first())
                db.session.commit()
        return redirect(url_for('manage_projects_bp.projects'))
    accounts = Account.query.all()
    users = User.query.all()
    return render_template('/projects/manage/form.html', template_mode='add', accounts=accounts, users=users)


@manage_projects_bp.route('/projects/edit/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def projects_edit(id):
    project = Project.query.filter_by(id=id).first()
    if 'submit-edit' in request.form:
        if project:
            project.name = request.form['name']
            project.duedate = request.form['duedate']
            project.account_id = request.form['account_id']
            project.users[:] = []
            db.session.commit()
            # Add Users
            user_ids = request.form.getlist("user_ids")
            for user_id in user_ids:
                exists = db.session.query(User.id).filter_by(id=user_id).scalar()
                if exists:
                    project.users.append(User.query.filter_by(id=user_id).first())
                    db.session.commit()
        return redirect(url_for('manage_projects_bp.projects'))
    accounts = Account.query.all()
    users = User.query.all()
    return render_template('/projects/manage/form.html', template_mode='edit', accounts=accounts, users=users, project=project)


@manage_projects_bp.route('/projects/delete/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def projects_delete(id):
    project = Project.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if project:
            db.session.delete(project)
            db.session.commit()
        return redirect(url_for('manage_projects_bp.projects'))
    accounts = Account.query.all()
    users = User.query.all()
    return render_template('/projects/manage/form.html', template_mode='delete', accounts=accounts, users=users, project=project)
