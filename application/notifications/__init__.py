from flask import Blueprint
from flask_login import current_user
from flask import current_app as app
#from .routes import notifications_bp, create_notification
from .apis import notifications_apis_bp
from .routes import notifications_bp
from .manage import manage_notifications_bp
#from ..models import User, MessageTemplate, Notification
#from .utils import create_notification, send_email_notification, send_sms_notification

app.register_blueprint(notifications_bp)
app.register_blueprint(manage_notifications_bp)
app.register_blueprint(notifications_apis_bp)
