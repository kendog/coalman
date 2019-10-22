from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
from .routes import notifications_bp, create_notification
from .apis import notifications_apis_bp
from ..models import db, Message, Archive

app.register_blueprint(notifications_bp)
app.register_blueprint(notifications_apis_bp)
