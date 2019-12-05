"""Routes for user authentication."""
from flask import redirect, render_template, Blueprint, request, url_for
from flask import current_app as app
from flask_security import roles_required, roles_accepted, current_user
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import User, MessageTemplate, Notification, Account
import smtplib
#from flask_mail import Message
from .. import mail
from .utils import create_notification, send_email_notification, send_sms_notification

# Blueprint Configuration
manage_notifications_bp = Blueprint('manage_notifications_bp', __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/manage')


@manage_notifications_bp.route('/notifications')
@roles_required('super-admin')
def notifications():
    notifications = Notification.query.all()
    return render_template('/notifications/manage/list.html', notifications=notifications)


@manage_notifications_bp.route('/notifications/add', methods=['POST', 'GET'])
@roles_required('super-admin')
def notifications_add():
    if 'submit-add' in request.form:
        create_notification(request.form['user_id'], request.form['project_id'], request.form['message_template_id'], request.form.get("notify_email"), request.form.get("notify_sms"))
        return redirect(url_for('manage_notifications_bp.notifications'))
    users = User.query.all()
    message_templates = MessageTemplate.query.all()
    return render_template('/notifications/manage/form.html', template_mode='add', users=users, message_templates=message_templates)


@manage_notifications_bp.route('/notifications/edit/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def notifications_edit(id):
    notification = Notification.query.filter_by(id=id).first()
    if 'submit-edit' in request.form:
        if notification:
            notification.user_id = request.form['user_id']
            notification.project_id = request.form['project_id']
            notification.message_template_id = request.form['message_template_id']
            db.session.commit()
            #send email/sms
            if request.form.get("notify_email"):
                send_email_notification(notification.id)
            if request.form.get("notify_sms"):
                send_sms_notification(notification.id)
        return redirect(url_for('manage_notifications_bp.notifications'))
    users = User.query.all()
    message_templates = MessageTemplate.query.all()
    return render_template('/notifications/manage/form.html', template_mode='edit', notification=notification, users=users, message_templates=message_templates)


@manage_notifications_bp.route('/notifications/delete/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def notifications_delete(id):
    notification = Notification.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if notification:
            db.session.delete(notification)
            db.session.commit()
        return redirect(url_for('manage_notifications_bp.notifications'))
    users = User.query.all()
    message_templates = MessageTemplate.query.all()
    return render_template('/notifications/manage/form.html', template_mode='delete', notification=notification, users=users, message_templates=message_templates)
