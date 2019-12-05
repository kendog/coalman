"""Routes for logged-in application."""
from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .routes import message_templates_bp
from .manage import manage_message_templates_bp

app.register_blueprint(message_templates_bp)
app.register_blueprint(manage_message_templates_bp)
