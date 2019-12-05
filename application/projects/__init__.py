"""Routes for logged-in application."""
from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .routes import projects_bp
from .manage import manage_projects_bp
from ..models import Project, Account
from sqlalchemy import or_, and_


app.register_blueprint(projects_bp)
app.register_blueprint(manage_projects_bp)


@app.context_processor
def inject_projects():
    projects = []
    if current_user.has_role('super-admin'):
        projects = Project.query.all()
    elif current_user.has_role('admin'):
        projects = Project.query\
            .join(Account)\
            .filter(and_(Account.id == Project.account_id, Account.id == current_user.account_id))\
            .all()
    elif current_user.is_authenticated:
        projects = current_user.projects
    return dict(current_projects=projects)
