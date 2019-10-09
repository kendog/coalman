from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .routes import apis_bp
from .v1_files import v1_files_bp
from .v1_tags import v1_tags_bp

app.register_blueprint(apis_bp)
app.register_blueprint(v1_files_bp)
app.register_blueprint(v1_tags_bp)
