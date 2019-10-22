"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import login_required
from flask import current_app as app
from flask_security import roles_required, roles_accepted, current_user
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..models import db, Project, Account


# Blueprint Configuration
projects_bp = Blueprint('projects_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@projects_bp.route('/projects')
@roles_required('super-admin')
def projects():
    projects = Project.query.all()
    return render_template('projects/list.html', projects=projects)



@projects_bp.route('/projects/add', methods=['POST', 'GET'])
@roles_required('super-admin')
def projects_add():
    if 'submit-add' in request.form:
        project = Project(name=request.form['name'], account_id=request.form['account_id'])
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('projects_bp.projects'))
    accounts = Account.query.all()
    return render_template('projects/form.html', template_mode='add', accounts=accounts)


@projects_bp.route('/projects/edit/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def projects_edit(id):
    project = Project.query.filter_by(id=id).first()
    if 'submit-edit' in request.form:
        if project:
            project.name = request.form['name']
            project.account_id = request.form['account_id']
            db.session.commit()
        return redirect(url_for('projects_bp.projects'))
    accounts = Account.query.all()
    return render_template('projects/form.html', template_mode='edit', accounts=accounts, project=project)


@projects_bp.route('/projects/delete/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def projects_delete(id):
    project = Project.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if project:
            db.session.delete(project)
            db.session.commit()
        return redirect(url_for('projects_bp.projects'))
    accounts = Account.query.all()
    return render_template('projects/form.html', template_mode='delete', accounts=accounts, project=project)
