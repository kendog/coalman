"""Routes for user authentication."""
from flask import redirect, render_template, Blueprint, request, url_for
from flask import current_app as app
from flask_security import roles_required, roles_accepted, current_user
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..db import db
from ..models import User, MessageTemplate, Notification, Account, Project
import smtplib
#from flask_mail import Message
from .. import mail
from .utils import create_notification, send_email_notification, send_sms_notification
from sqlalchemy import or_, and_

# Blueprint Configuration
notifications_bp = Blueprint('notifications_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@notifications_bp.route('/notifications')
@roles_accepted('admin','super-admin')
def notifications():
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_notifications_bp.notifications'))

    notifications = Notification.query\
        .join(Project)\
        .filter(and_(Notification.project_id == Project.id, Project.account_id == current_user.account_id))\
        .all()

    return render_template('/notifications/list.html', notifications=notifications)


@notifications_bp.route('/notifications/add', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def notifications_add():
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_notifications_bp.notifications_add'))

    if 'submit-add' in request.form:
        create_notification(request.form['user_id'], request.form['project_id'], request.form['message_template_id'], request.form.get("notify_email"), request.form.get("notify_sms"))
        return redirect(url_for('notifications_bp.notifications'))
    users = User.query.filter(User.account_id == current_user.account_id).all()
    message_templates = MessageTemplate.query\
        .filter(MessageTemplate.account_id == current_user.account_id)\
        .all()
    return render_template('/notifications/form.html', template_mode='add', users=users, message_templates=message_templates)


@notifications_bp.route('/notifications/edit/<id>', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def notifications_edit(id):
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_notifications_bp.notifications_edit',id=id))

    notification = Notification.query\
        .join(Project)\
        .filter(and_(Notification.id == id, Notification.project_id == Project.id, Project.account_id == current_user.account_id))\
        .first()

    if not notification:
        return redirect(url_for('notifications_bp.notifications'))

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
        return redirect(url_for('notifications_bp.notifications'))
    users = User.query.filter(User.account_id == current_user.account_id).all()
    message_templates = MessageTemplate.query\
        .filter(MessageTemplate.account_id == current_user.account_id)\
        .all()
    return render_template('/notifications/form.html', template_mode='edit', notification=notification, users=users, message_templates=message_templates)


@notifications_bp.route('/notifications/delete/<id>', methods=['POST', 'GET'])
@roles_accepted('admin','super-admin')
def notifications_delete(id):
    if current_user.has_role('super-admin'):
        return redirect(url_for('manage_notifications_bp.notifications_delete',id=id))

    notification = Notification.query\
        .join(Project)\
        .filter(and_(Notification.id == id, Notification.project_id == Project.id, Project.account_id == current_user.account_id))\
        .first()

    if not notification:
        return redirect(url_for('notifications_bp.notifications'))

    if 'submit-delete' in request.form:
        if notification:
            db.session.delete(notification)
            db.session.commit()
        return redirect(url_for('notifications_bp.notifications'))
    users = User.query.filter(User.account_id == current_user.account_id).all()
    message_templates = MessageTemplate.query\
        .filter(MessageTemplate.account_id == current_user.account_id)\
        .all()
    return render_template('/notifications/form.html', template_mode='delete', notification=notification, users=users, message_templates=message_templates)
