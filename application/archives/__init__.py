"""Routes for logged-in application."""
from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .routes import archives_bp
from .apis import archives_apis_bp

app.register_blueprint(archives_bp)
app.register_blueprint(archives_apis_bp)
