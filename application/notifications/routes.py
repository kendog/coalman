"""Routes for user authentication."""
from flask import redirect, render_template, Blueprint, request, url_for
from flask import current_app as app
from flask_security import roles_required
#from .assets import compile_auth_assets
#from .forms import LoginForm, SignupForm
from ..models import db, User, MessageTemplate, Notification, NotificationStatus
import smtplib
from flask_mail import Message
from .. import mail

# Blueprint Configuration
notifications_bp = Blueprint('notifications_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@notifications_bp.route('/notifications')
@roles_required('super-admin')
def notifications():
    notifications = Notification.query.all()
    return render_template('notifications/list.html', notifications=notifications)


@notifications_bp.route('/notifications/add', methods=['POST', 'GET'])
@roles_required('super-admin')
def notifications_add():
    if 'submit-add' in request.form:
        create_notification(request.form['user_id'], request.form['message_id'], request.form.get("notify_email"), request.form.get("notify_sms"))
        return redirect(url_for('notifications_bp.notifications'))
    users = User.query.all()
    messages = MessageTemplate.query.all()
    return render_template('notifications/form.html', template_mode='add', users=users, messages=messages)


@notifications_bp.route('/notifications/edit/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def notifications_edit(id):
    notification = Notification.query.filter_by(id=id).first()
    if 'submit-edit' in request.form:
        if notification:
            notification.user_id = request.form['user_id']
            notification.message_id = request.form['message_id']
            db.session.commit()
            #send email/sms
            if request.form.get("notify_email"):
                send_email_notification(notification.id)
            if request.form.get("notify_sms"):
                send_sms_notification(notification.id)
        return redirect(url_for('notifications_bp.notifications'))
    users = User.query.all()
    messages = MessageTemplate.query.all()
    return render_template('notifications/form.html', template_mode='edit', notification=notification, users=users, messages=messages)


@notifications_bp.route('/notifications/delete/<id>', methods=['POST', 'GET'])
@roles_required('super-admin')
def notifications_delete(id):
    notification = Notification.query.filter_by(id=id).first()
    if 'submit-delete' in request.form:
        if notification:
            db.session.delete(notification)
            db.session.commit()
        return redirect(url_for('notifications_bp.notifications'))
    users = User.query.all()
    messages = MessageTemplate.query.all()
    return render_template('notifications/form.html', template_mode='delete', notification=notification, users=users, messages=messages)


def create_notification(user_id, message_id, send_email, send_sms):
    notification_status = NotificationStatus.query.first()
    notification = Notification(user_id=user_id, message_id=message_id, notification_status_id=notification_status.id)
    db.session.add(notification)
    db.session.commit()
    #send email/sms
    if send_email:
        send_email_notification(notification.id)
    if send_sms:
        send_sms_notification(notification.id)
    return redirect(url_for('notifications_bp.notifications'))


def send_email_notification(notification_id):

    notification = Notification.query.filter_by(id=notification_id).first()

    # Build the Mail
    user = User.query.filter_by(id=notification.user_id).first()
    message_template = MessageTemplate.query.filter_by(id=notification.message_id).first()

    msg = Message(message_template.subject, sender=app.config['MAIL_USERNAME'], recipients=[user.email])
    msg.body = message_template.message
    mail.send(msg)

    notification.notification_status_id = 1
    db.session.commit()


def send_sms_notification(notification_id):
    notification = Notification.query.filter_by(id=notification_id).first()
    notification.notification_status_id = 1
    db.session.commit()
