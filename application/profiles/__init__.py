from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .routes import profiles_bp

app.register_blueprint(profiles_bp)
