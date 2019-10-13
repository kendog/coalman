"""Routes for user authentication."""
from flask import redirect, render_template, Blueprint, request, url_for
from flask import current_app as app
from flask_security import roles_required
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..models import db, Message
import smtplib


# Blueprint Configuration
notifications_bp = Blueprint('notifications_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@notifications_bp.route('/message/edit', methods=['POST', 'GET'])
@roles_required('admin')
def message_edit():
    message = Message.query.first()
    if 'submit-edit' in request.form and message:
        message.subject = request.form.get('subject')
        message.message = request.form.get('message')
        db.session.commit()
        return redirect(url_for('messages_bp.message_edit', message=message))
    return render_template('messages/form.html', message=message)

#@messages_bp.route('/notifications/<uuid>', methods=['POST', 'GET'])
#@roles_required('admin')
