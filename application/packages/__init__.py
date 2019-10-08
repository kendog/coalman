"""Routes for logged-in application."""
from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .routes import packages_bp

app.register_blueprint(packages_bp)
