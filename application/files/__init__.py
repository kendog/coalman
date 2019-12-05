"""Routes for logged-in application."""
from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .routes import files_bp
from .apis import files_apis_bp
from .manage import manage_files_bp
from .dropzone import dropzone_bp
from ..models import Project, Account, File
from sqlalchemy import or_, and_

app.register_blueprint(files_bp)
app.register_blueprint(files_apis_bp)
app.register_blueprint(manage_files_bp)
app.register_blueprint(dropzone_bp)


@app.context_processor
def inject_projects():
    files = []
    if current_user.has_role('super-admin'):
        files = File.query.all()
    elif current_user.has_role('admin'):
        files = File.query\
            .join(Project)\
            .filter(and_(File.project_id == Project.id, Project.account_id == current_user.account_id))\
            .all()
    elif current_user.is_authenticated:
        files = File.query.filter_by(creator_id=current_user.id).all()

    return dict(current_files=files)
