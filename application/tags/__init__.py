"""Routes for logged-in application."""
from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .routes import tags_bp
from .apis import tags_apis_bp

app.register_blueprint(tags_bp)
app.register_blueprint(tags_apis_bp)
